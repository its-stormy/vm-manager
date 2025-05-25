# vm-manager
# VBoxAutoManager

**VBoxAutoManager** est un script Python avancé qui permet de gérer facilement des machines virtuelles VirtualBox en ligne de commande : création, suppression, démarrage, arrêt, clonage, et plus encore.

## 📦 Fonctionnalités

- Créer une VM avec paramètres personnalisés (RAM, CPU, disque, ISO, réseau)
- Démarrer/arrêter une VM (mode GUI ou headless)
- Supprimer une VM avec ses disques
- Cloner une VM existante
- Lister les VMs (avec détails si souhaité)
- Afficher les informations d'une VM (en texte ou JSON)

## 📌 Prérequis

- [VirtualBox](https://www.virtualbox.org/) installé (et `VBoxManage` disponible dans le PATH)
- Python 3.6+

## 🔧 Installation

```bash
git clone https://github.com/votre-utilisateur/vbox-automanager.git
cd vbox-automanager
pip install -r requirements.txt
