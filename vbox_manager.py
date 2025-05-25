#!/usr/bin/env python3
import subprocess
import argparse
import sys
import os
import json

class VirtualBoxManager:
    def __init__(self):
        self.check_virtualbox_installed()

    def check_virtualbox_installed(self):
        try:
            subprocess.run(["VBoxManage", "--version"], check=True, 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            print("VirtualBox n'est pas installé ou VBoxManage n'est pas dans le PATH.")
            sys.exit(1)
        except subprocess.CalledProcessError:
            print("Erreur lors de l'exécution de VBoxManage.")
            sys.exit(1)

    def create_vm(self, name, os_type, ram, cpus, disk_size, disk_type, 
                 iso_path=None, start_vm=False, network="nat"):
        """Crée une nouvelle machine virtuelle"""
        print(f"Création de la VM {name}...")
        
        # Validation des paramètres
        if disk_size < 1000:
            print("Erreur: La taille du disque doit être d'au moins 1000 MB.")
            return False

        try:
            # Création de la VM
            subprocess.run(["VBoxManage", "createvm", "--name", name, 
                          "--ostype", os_type, "--register"], check=True)
            
            # Configuration de base
            subprocess.run(["VBoxManage", "modifyvm", name, "--memory", str(ram)], check=True)
            subprocess.run(["VBoxManage", "modifyvm", name, "--cpus", str(cpus)], check=True)
            
            # Création du disque dur
            disk_file = f"{name}_disk.{disk_type.lower()}"
            subprocess.run([
                "VBoxManage", "createmedium", "disk", 
                "--filename", disk_file, 
                "--size", str(disk_size), 
                "--format", disk_type
            ], check=True)
            
            # Configuration du contrôleur de stockage
            subprocess.run(["VBoxManage", "storagectl", name, 
                           "--name", "SATA", "--add", "sata", "--controller", "IntelAhci"], check=True)
            subprocess.run([
                "VBoxManage", "storageattach", name, 
                "--storagectl", "SATA", 
                "--port", "0", 
                "--device", "0", 
                "--type", "hdd", 
                "--medium", disk_file
            ], check=True)
            
            # Configuration ISO si fournie
            if iso_path:
                if not os.path.exists(iso_path):
                    print(f"Erreur: Le fichier ISO {iso_path} n'existe pas.")
                    return False
                
                subprocess.run(["VBoxManage", "storagectl", name, 
                              "--name", "IDE", "--add", "ide"], check=True)
                subprocess.run([
                    "VBoxManage", "storageattach", name, 
                    "--storagectl", "IDE", 
                    "--port", "0", 
                    "--device", "0", 
                    "--type", "dvddrive", 
                    "--medium", iso_path
                ], check=True)
            
            # Configuration réseau
            self.configure_network(name, network)
            
            print(f"VM {name} créée avec succès!")
            
            if start_vm:
                self.start_vm(name)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la création de la VM: {e}")
            return False

    def configure_network(self, vm_name, network_type):
        """Configure le réseau pour une VM"""
        if network_type.lower() == "nat":
            subprocess.run(["VBoxManage", "modifyvm", vm_name, "--nic1", "nat"], check=True)
        elif network_type.lower() == "bridged":
            subprocess.run(["VBoxManage", "modifyvm", vm_name, "--nic1", "bridged", "--bridgeadapter1", "eth0"], check=True)
        elif network_type.lower() == "hostonly":
            subprocess.run(["VBoxManage", "modifyvm", vm_name, "--nic1", "hostonly", "--hostonlyadapter1", "vboxnet0"], check=True)
        else:
            subprocess.run(["VBoxManage", "modifyvm", vm_name, "--nic1", "none"], check=True)

    def start_vm(self, name, headless=False):
        """Démarre une VM"""
        try:
            print(f"Démarrage de la VM {name}...")
            mode = "headless" if headless else "gui"
            subprocess.run(["VBoxManage", "startvm", name, "--type", mode], check=True)
            print(f"VM {name} démarrée en mode {mode}.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du démarrage de la VM: {e}")
            return False

    def stop_vm(self, name, force=False):
        """Arrête une VM"""
        try:
            print(f"Arrêt de la VM {name}...")
            mode = "poweroff" if force else "acpipowerbutton"
            subprocess.run(["VBoxManage", "controlvm", name, mode], check=True)
            print(f"VM {name} arrêtée.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'arrêt de la VM: {e}")
            return False

    def delete_vm(self, name):
        """Supprime une VM"""
        try:
            print(f"Suppression de la VM {name}...")
            subprocess.run(["VBoxManage", "unregistervm", name, "--delete"], check=True)
            print(f"VM {name} supprimée.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la suppression de la VM: {e}")
            return False

    def list_vms(self, details=False):
        """Liste toutes les VMs avec ou sans détails"""
        try:
            print("Liste des VMs disponibles:")
            result = subprocess.run(["VBoxManage", "list", "vms"], 
                                   check=True, capture_output=True, text=True)
            print(result.stdout)
            
            if details:
                print("\nDétails des VMs en cours d'exécution:")
                subprocess.run(["VBoxManage", "list", "runningvms"], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la liste des VMs: {e}")
            return False

    def show_vm_info(self, name, output_format="text"):
        """Affiche les détails d'une VM spécifique"""
        try:
            if output_format == "json":
                info = self._get_vm_info_json(name)
                print(json.dumps(info, indent=2))
            else:
                print(f"\n=== Informations détaillées pour la VM {name} ===\n")
                print("Configuration générale:")
                subprocess.run(["VBoxManage", "showvminfo", name], check=True)
                
                print("\nConfiguration réseau:")
                subprocess.run(["VBoxManage", "showvminfo", name, "--details", "--networking"], check=True)
                
                print("\nDisques attachés:")
                subprocess.run(["VBoxManage", "showvminfo", name, "--storage"], check=True)
            return True
        except subprocess.CalledProcessError:
            print(f"Erreur: La VM {name} n'existe pas ou n'est pas accessible.")
            return False

    def _get_vm_info_json(self, name):
        """Récupère les infos de la VM au format JSON"""
        result = subprocess.run(["VBoxManage", "showvminfo", name, "--machinereadable"], 
                               check=True, capture_output=True, text=True)
        
        info = {}
        for line in result.stdout.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                info[key.strip('"')] = value.strip('"')
        
        return info

    def clone_vm(self, original_name, new_name):
        """Clone une VM existante"""
        try:
            print(f"Clonage de la VM {original_name} vers {new_name}...")
            subprocess.run(["VBoxManage", "clonevm", original_name, "--name", new_name, "--register"], check=True)
            print(f"VM {new_name} créée à partir de {original_name}.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du clonage: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Gestionnaire de machines virtuelles VirtualBox")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Création d'une VM
    create_parser = subparsers.add_parser('create', help='Créer une nouvelle VM')
    create_parser.add_argument('--name', required=True, help='Nom de la VM')
    create_parser.add_argument('--os-type', required=True, help='Type de OS (ex: Linux_64, Windows10_64)')
    create_parser.add_argument('--ram', type=int, required=True, help='Mémoire RAM en MB')
    create_parser.add_argument('--cpus', type=int, required=True, help='Nombre de CPUs')
    create_parser.add_argument('--disk-size', type=int, required=True, help='Taille du disque en MB')
    create_parser.add_argument('--disk-type', default="VDI", choices=["VDI", "VHD", "VMDK"], 
                              help='Type de disque (VDI, VHD, VMDK)')
    create_parser.add_argument('--iso', help='Chemin vers le fichier ISO d\'installation')
    create_parser.add_argument('--start', action='store_true', help='Démarrer la VM après création')
    create_parser.add_argument('--network', default="nat", choices=["nat", "bridged", "hostonly", "none"], 
                              help='Type de réseau (nat, bridged, hostonly, none)')

    # Gestion des VMs
    start_parser = subparsers.add_parser('start', help='Démarrer une VM')
    start_parser.add_argument('--name', required=True, help='Nom de la VM')
    start_parser.add_argument('--headless', action='store_true', help='Démarrer en mode headless')

    stop_parser = subparsers.add_parser('stop', help='Arrêter une VM')
    stop_parser.add_argument('--name', required=True, help='Nom de la VM')
    stop_parser.add_argument('--force', action='store_true', help='Forcer l\'arrêt (poweroff)')

    delete_parser = subparsers.add_parser('delete', help='Supprimer une VM')
    delete_parser.add_argument('--name', required=True, help='Nom de la VM')

    list_parser = subparsers.add_parser('list', help='Lister toutes les VMs')
    list_parser.add_argument('--details', action='store_true', help='Afficher les détails des VMs en cours d\'exécution')

    info_parser = subparsers.add_parser('info', help='Afficher les informations d\'une VM')
    info_parser.add_argument('--name', required=True, help='Nom de la VM')
    info_parser.add_argument('--format', choices=["text", "json"], default="text", 
                            help='Format de sortie (text ou json)')

    clone_parser = subparsers.add_parser('clone', help='Cloner une VM existante')
    clone_parser.add_argument('--original', required=True, help='Nom de la VM originale')
    clone_parser.add_argument('--new-name', required=True, help='Nom de la nouvelle VM')

    args = parser.parse_args()
    vbm = VirtualBoxManager()

    if args.command == 'create':
        vbm.create_vm(
            name=args.name,
            os_type=args.os_type,
            ram=args.ram,
            cpus=args.cpus,
            disk_size=args.disk_size,
            disk_type=args.disk_type,
            iso_path=args.iso,
            start_vm=args.start,
            network=args.network
        )
    elif args.command == 'start':
        vbm.start_vm(name=args.name, headless=args.headless)
    elif args.command == 'stop':
        vbm.stop_vm(name=args.name, force=args.force)
    elif args.command == 'delete':
        vbm.delete_vm(name=args.name)
    elif args.command == 'list':
        vbm.list_vms(details=args.details)
    elif args.command == 'info':
        vbm.show_vm_info(name=args.name, output_format=args.format)
    elif args.command == 'clone':
        vbm.clone_vm(original_name=args.original, new_name=args.new_name)

if __name__ == "__main__":
    main()
