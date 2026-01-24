import logging
import xmlrpc.client
from typing import Any

from src.core.settings import get_settings
from src.schemas.api.odoo import InvoiceCreatePayload
from src.utils.exceptions import OdooFaultError, OdooProtocolError

settings = get_settings()
logger = logging.getLogger(__name__)


class OdooClient:
    def __init__(self):
        self.url = f"https://{settings.ODOO_HOST}:{settings.ODOO_PORT}/xmlrpc/2"  # NOTE: https is required even if port 443 is specified  # noqa: E501
        self.db = settings.ODOO_DATABASE
        self.username = settings.ODOO_USER
        self.api_key = settings.ODOO_API_KEY

        self.common = xmlrpc.client.ServerProxy(f"{self.url}/common")
        self.uid = self._call(
            self.common.authenticate, self.db, self.username, self.api_key, {}
        )
        logger.info(f"Authenticated with Odoo, UID: {self.uid}")

        if not self.uid:
            raise OdooFaultError("Authentication failed with Odoo")

        self.models = xmlrpc.client.ServerProxy(f"{self.url}/object")

    def version(self) -> str:
        return self.common.version()

    def _call(self, service_method, *args, **kwargs) -> Any:
        """
        Make a RPC call to Odoo.
        Args:
            service_method: the method to call
            *args: the arguments to pass to the method
            **kwargs: the keyword arguments to pass to the method

        Returns:
            Any: the result of the RPC call
        """
        try:
            return service_method(*args, **kwargs)
        except xmlrpc.client.ProtocolError as err:
            details = {
                "url": err.url,
                "errcode": err.errcode,
                "errmsg": err.errmsg,
                "headers": dict(err.headers) if err.headers else {},
            }
            logger.error(
                f"Odoo Protocol Error: {err.errcode} {err.errmsg}", extra=details
            )
            raise OdooProtocolError(
                f"Odoo error: {err.errcode} {err.errmsg}, details: {details}",
                details=details,
            ) from err

        except xmlrpc.client.Fault as err:
            details = {
                "faultCode": err.faultCode,
                "faultString": err.faultString,
            }
            logger.error(
                f"Odoo Fault: {err.faultCode} - {err.faultString}", extra=details
            )
            raise OdooFaultError(
                f"Odoo Fault: {err.faultString}", details=details
            ) from err

        except Exception as err:
            logger.exception("Unexpected error during Odoo RPC call")
            raise err

    def get_data(
        self,
        model: str,
        fields: list[str],
        domain: list,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        return self._call(
            self.models.execute_kw,
            self.db,
            self.uid,
            self.api_key,
            model,
            "search_read",
            [domain],
            {"fields": fields, "limit": limit, "offset": offset},
        )

    def create_data(self, model: str, values: dict) -> int:
        return self._call(
            self.models.execute_kw,
            self.db,
            self.uid,
            self.api_key,
            model,
            "create",
            [values],
        )

    def update_data(self, model: str, id: int, values: dict) -> bool:
        return self._call(
            self.models.execute_kw,
            self.db,
            self.uid,
            self.api_key,
            model,
            "write",
            [[id], values],
        )

    def delete_data(self, model: str, id: int) -> bool:
        return self._call(
            self.models.execute_kw,
            self.db,
            self.uid,
            self.api_key,
            model,
            "unlink",
            [[id]],
        )

    def get_count(self, model: str, domain: list) -> int:
        return self._call(
            self.models.execute_kw,
            self.db,
            self.uid,
            self.api_key,
            model,
            "search_count",
            [domain],
        )

    def get_contacts(
        self, is_company: bool = False, limit: int = 100, offset: int = 0
    ) -> list[dict]:
        """
        :param is_company: if True, return companies, if False, return contacts
        :param limit: number of records to return
        :param offset: number of records to skip
        """
        return self.get_data(
            model="res.partner",
            fields=[
                "id",
                "name",
                "email",
                "display_name",
                "company_id",
            ],
            domain=[("is_company", "=", is_company)],
            limit=limit,
            offset=offset,
        )

    def create_contact(
        self,
        name: str,
        email: str,
        company_name: str,
    ) -> int:
        """
        Create a contact in Odoo.
        Args:
            name: str
            email: str
            company_name: str

        Returns:
            int: Odoo contact ID
        """
        company_id = self.create_data(
            model="res.partner",
            values={
                "name": company_name,
                "is_company": True,
            },
        )
        return self.create_data(
            model="res.partner",
            values={
                "name": name,
                "email": email,
                "is_company": False,
                "parent_id": company_id,
            },
        )

    def get_invoices(
        self, domain: list | None = None, limit: int = 100, offset: int = 0
    ) -> list[dict]:
        """
        Get invoices from Odoo.
        Args:
            domain: list of tuples for filtering
            limit: max number of records
            offset: number of records to skip

        Returns:
            list[dict]: list of invoices
        """
        if domain is None:
            domain = [("move_type", "=", "out_invoice")]
        return self.get_data(
            model="account.move",
            fields=[
                "id",
                "name",
                "partner_id",
                "invoice_date",
                "amount_total",
                "state",
                "move_type",
            ],
            domain=domain,
            limit=limit,
            offset=offset,
        )

    def get_partners(
        self, domain: list | None = None, limit: int = 100, offset: int = 0
    ) -> list[dict]:
        if domain is None:
            domain = []
        return self.get_data(
            model="res.partner",
            fields=["id", "name", "email", "display_name", "company_id"],
            domain=domain,
            limit=limit,
            offset=offset,
        )

    def create_invoice(
        self,
        partner_id: int,
        invoice_lines: list[InvoiceCreatePayload],
        move_type: str = "out_invoice",
        **kwargs,
    ) -> int:
        """
        Create an invoice in Odoo.
        Args:
            partner_id: Odoo partner ID
            invoice_lines: list of dicts with keys like 'product_id', 'quantity', 'price_unit'
            move_type: type of the move (default: out_invoice)
            **kwargs: additional fields for account.move

        Returns:
            int: Odoo invoice ID
        """
        lines = [(0, 0, line.model_dump(mode="json")) for line in invoice_lines]

        values = {
            "partner_id": partner_id,
            "move_type": move_type,
            "invoice_line_ids": lines,
            **kwargs,
        }
        return self.create_data(model="account.move", values=values)
