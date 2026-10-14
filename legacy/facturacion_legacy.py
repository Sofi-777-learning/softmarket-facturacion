# Código ORIGINAL de SoftMarket (antes del refactor). No usar: solo referencia.
import smtplib
import sqlite3


class GestorFacturas:
    def crear_factura(self, cliente, items, tipo_cliente, pais):
        total = 0
        for it in items:
            total += it["precio"] * it["cant"]
        if tipo_cliente == "normal":
            desc = 0
        elif tipo_cliente == "vip":
            desc = total * 0.10
        elif tipo_cliente == "mayorista":
            desc = total * 0.20
        else:
            desc = 0
        if pais == "CO":
            iva = (total - desc) * 0.19
        elif pais == "EC":
            iva = (total - desc) * 0.12
        else:
            iva = 0
        total_final = total - desc + iva
        conn = sqlite3.connect("/var/data/softmarket.db")
        conn.execute("INSERT INTO facturas VALUES (?,?,?)", (cliente["id"], total_final, pais))
        conn.commit()
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.login("admin@softmarket.com", "123456")
        server.sendmail("admin@softmarket.com", cliente["email"], "Su factura: %s" % total_final)
        return total_final
