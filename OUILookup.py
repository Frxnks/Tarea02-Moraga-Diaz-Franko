import requests
import sys
import getopt
import subprocess
import platform
from typing import List, Dict, Any, Optional
from pprint import pprint

# Franko Moraga Diaz
# Bruno Gonzales Luke
# Ignacio Guerrero Gómez

# Funcion para conseguir informacion de las MAC en la url.
def fetch_mac_data(mac_address: str) -> Dict[str, Any]:
    url = f"https://api.maclookup.app/v2/macs/{mac_address}"
    try:
        response = requests.get(url)
        data = response.json()
        return {
            "MAC address": mac_address,
            "Fabricante": data.get('company') if data.get('success') and data.get('found') else "Not Found",
            "Tiempo de respuesta": int(response.elapsed.total_seconds() * 1000)
        }
    except requests.exceptions.RequestException as e:
        return {
            "MAC address": mac_address,
            "error": str(e)
        }

# Funcion ARP, consigue todos los datos de la url.
def parse_arp_output(output: str) -> List[str]:
    lines = output.splitlines()
    mac_addresses = []
    for line in lines:
        parts = line.split()
        if len(parts) > 1 and ("-" in parts[1] or ":" in parts[1]):
            mac_addresses.append(parts[1])
    return mac_addresses

# Funcion para obtener MAC's del sistema.
def get_arp_table() -> List[str]:
    try:
        if platform.system() == "Windows":
            result = subprocess.check_output("arp -a", shell=True).decode("latin-1")
        else:
            result = subprocess.check_output("arp -n", shell=True).decode("utf-8")
        return parse_arp_output(result)
    except subprocess.CalledProcessError as e:
        return []

# Consulta de MAC especifica.
def consulta_mac(mac_address: str) -> Optional[Dict[str, Any]]:
    return fetch_mac_data(mac_address)

# Consulta los valores de la tabla ARP.
def consulta_arp() -> List[Dict[str, Any]]:
    mac_addresses = get_arp_table()
    return [fetch_mac_data(mac) for mac in mac_addresses]

# Mensaje de ayuda.
def mostrar_ayuda() -> str:
    return (
        "Uso: OUILookup.py --mac <mac> | --arp | [--help]\n"
        " --mac : MAC a consultar. Ejemplo: aa:bb:cc:00:00:00\n"
        " --arp : Mostrar los fabricantes disponibles en la tabla ARP\n"
        " --help: Mostrar este mensaje de ayuda"
    )

# funcion principal. (donde se ejecuta las funciones)
def main(args: List[str]) -> Optional[str]:
    try:
        opts, _ = getopt.getopt(args, "hm:a", ["help", "mac=", "arp"])
    except getopt.GetoptError:
        return mostrar_ayuda()

    for opt, arg in opts:
        if opt in ("-m", "--mac"):
            return consulta_mac(arg)
        elif opt == "--arp":
            return consulta_arp()
        elif opt in ("-h", "--help"):
            return mostrar_ayuda()

    return mostrar_ayuda()

if __name__ == "__main__":
    result = main(sys.argv[1:])
    if result:
        pprint(result)