from escpos.printer import Network, Usb

from app.core.config import settings
from app.models.transaction import Transaction


def _build_receipt_text(transaction: Transaction) -> list[str]:
    lines = [
        settings.store_name,
        f"Invoice: {transaction.invoice_no}",
        f"Date: {transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "-------------------------------",
    ]

    for item in transaction.items:
        lines.append(
            f"{item.product_name} x{item.qty} @ {float(item.selling_price):.2f}"
        )
        lines.append(f"  = {float(item.subtotal):.2f}")

    lines.extend(
        [
            "-------------------------------",
            f"TOTAL  : {float(transaction.total_amount):.2f}",
            f"PAYMENT: {float(transaction.payment_amount):.2f}",
            f"CHANGE : {float(transaction.change_amount):.2f}",
            "\nThank you for shopping!",
        ]
    )
    return lines


def print_transaction_receipt(transaction: Transaction) -> None:
    if settings.printer_mode == "usb":
        printer = Usb(
            idVendor=settings.printer_usb_vendor_id,
            idProduct=settings.printer_usb_product_id,
            timeout=settings.printer_usb_timeout_ms,
        )
    else:
        printer = Network(settings.printer_network_host, settings.printer_network_port)

    lines = _build_receipt_text(transaction)
    printer.set(align="center", bold=True, width=2, height=2)
    printer.text(f"{settings.store_name}\n")
    printer.set(align="left", bold=False, width=1, height=1)
    for line in lines[1:]:
        printer.text(f"{line}\n")
    printer.text("\n\n")
    printer.cut()
