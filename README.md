# LiXee Linky Indicator

Un indicateur pour la barre de tâche du bureau Linux qui affiche la consommation électrique en temps réel depuis un compteur Linky via une **[LiXee Box](https://lixee.fr/fr/)**.

## Fonctionnalités

- Affichage de la puissance apparente instantanée (VA) dans la barre de tâche
- Icône colorée selon les seuils de consommation :
  - 🟢 **Verte** — injection sur le réseau (production solaire)
  - 🟡 **Jaune** — consommation modérée
  - 🔴 **Rouge** — forte consommation
- Rechargement à chaud de la configuration
- Compatible GNOME, KDE, XFCE, budgie, etc. (tout bureau supportant AppIndicator)

## Prérequis

### Paquets système

```bash
# Debian / Ubuntu / Linux Mint
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 python3-requests

# Fedora
sudo dnf install python3-gobject gtk3 libappindicator-gtk3 python3-requests

# Arch Linux
sudo pacman -S python-gobject gtk3 libappindicator-gtk3 python-requests
```

## Installation

```bash
git clone https://github.com/Cyrille37/Lixee-Linky-indicator.git
cd Lixee-Linky-indicator
pip install .
```

### Exécution sans installation

```bash
python3 lixee-linky-indicator.py
```

## Configuration

Copiez le fichier modèle puis éditez-le :

```bash
cp .lixee-linky-indicator.example ~/.lixee-linky-indicator
nano ~/.lixee-linky-indicator
```

```ini
# Adresse IP de votre LiXee Box (obligatoire)
LIXEEBOX_IP=192.168.1.xx

# Intervalle de rafraîchissement en secondes (1-1800, défaut: 5)
REFRESH_SECONDS=5

# Seuils de puissance pour les couleurs de l'icône (en VA)
LOW_THRESHOLD=1      # En dessous : icône verte
HIGH_THRESHOLD=200   # Au-dessus : icône rouge
```

Le fichier est relu à chaud : modifiez-le, les changements s'appliquent sans redémarrer l'application.

## Utilisation

```bash
# Depuis le PATH (après pip install)
lixee-linky-indicator

# Ou via le module Python
python -m lixee_linky_indicator
```

L'indicateur apparaît dans la barre de notification.

Clic gauche pour le menu:
- **Quitter** pour fermer.

### Démarrage automatique

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/lixee-linky-indicator.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=LiXee Linky Indicator
Exec=lixee-linky-indicator
X-GNOME-Autostart-enabled=true
EOF
```

## Licence

Ce projet est distribué selon les termes de la **WTFPL** — voir le fichier [LICENSE](LICENSE) ou [wtfpl.net](https://www.wtfpl.net/).

## Crédits

- Développé par [Cyrille37](https://github.com/Cyrille37)
- Icônes : [FontAwesome](https://fontawesome.com/) (Solar Panel)
