# Résumé des Points Clés du Référentiel Azure AI Foundry

Ce document résume les points clés du référentiel d'exemples Azure AI Foundry pour aider les utilisateurs à comprendre rapidement l'architecture et les fonctionnalités du projet.

---

## 📋 Aperçu du Référentiel

**Azure AI Foundry Documentation Samples** est le référentiel officiel de code d'exemple pour la documentation Azure AI Foundry. Il comprend :

- Des exemples complets de bout en bout
- Des extraits de code pour les tâches de développement courantes
- Des Jupyter Notebooks
- Des exemples de code multilingues

**Objectif** : Permettre aux utilisateurs de tester différents scénarios Azure AI Foundry sur leur machine locale.

---

## 🛠️ Fonctionnalités et Exemples Principaux

### 1. Exemples de Service AI Agent (Python)

| Nom de l'Outil | Description |
|----------------|-------------|
| **quickstart.py** | Exemple de démarrage rapide montrant la configuration et l'utilisation de base |
| **basic_agent.py** | Configuration d'agent de base (sans outils supplémentaires) |
| **azure_ai_search.py** | Intégration de la base de connaissances Azure AI Search |
| **bing_grounding.py** | Utilisation de Bing pour l'ancrage des données |
| **code_interpreter** | Outil d'interpréteur de code |
| **file_search.py** | Fonctionnalité de téléchargement et de gestion de fichiers |
| **functions_calling.py** | Démonstration d'appel de fonctions locales |
| **azure_functions.py** | Appel de fonctions Azure durables |
| **logic_apps.py** | Intégration de flux de travail Logic Apps |
| **enterprise_search.py** | Intégration de recherche d'entreprise |
| **openapi** | Appels d'API externes (spécification OpenAPI) |

### 2. Exemples de Modèles Mistral AI

- Exemples de code pour utiliser les modèles Mistral AI sur la plateforme Azure Foundry
- Prise en charge du gestionnaire de paquets `uv` ou `pip`
- Intégration Jupyter Notebook disponible

---

## 💻 Langages de Programmation Pris en Charge

Le référentiel fournit des exemples dans plusieurs langages de programmation :

- **Python** - Langage d'exemple principal
- **JavaScript** / **TypeScript**
- **C#**
- **Java**
- **API REST**

---

## 🏗️ Configuration de l'Infrastructure (Infrastructure as Code)

Azure AI Agent Service propose trois modes de déploiement :

### Configuration de Base (Basic Setup)
- Compatible avec OpenAI Assistants
- Utilise le stockage intégré de la plateforme pour gérer l'état de l'agent
- Prend en charge les modèles et outils non-OpenAI (comme Azure AI Search, Bing)
- **Exemples** : `40-basic-agent-setup`, `42-basic-agent-setup-with-customization`

### Configuration Standard (Standard Setup)
- Inclut toutes les fonctionnalités de la configuration de base
- Permet d'utiliser vos propres ressources Azure pour stocker les données client
- Les fichiers, fils de conversation et stockage vectoriel sont tous stockés dans vos propres ressources
- **Exemple** : `41-standard-agent-setup`

### Configuration Standard avec Réseau Virtuel Personnel (BYO Virtual Network)
- Fonctionne entièrement au sein de votre propre réseau virtuel
- Contrôle strict du flux de données pour prévenir l'exfiltration de données
- **Exemple** : `15-private-network-standard-agent-setup`

### Autres Options de Configuration
| Configuration | Description |
|---------------|-------------|
| `00-basic` | Configuration de base Azure AI Foundry |
| `01-connections` | Configuration des connexions |
| `10-private-network-basic` | Configuration de base du réseau privé |
| `20-user-assigned-identity` | Identité gérée assignée par l'utilisateur |
| `25-entraid-passthrough` | Authentification pass-through Entra ID |
| `30-customer-managed-keys` | Clés gérées par le client |
| `45-basic-agent-bing` | Agent de base avec Bing |

---

## 📚 Points Clés du Guide de Contribution

### Prérequis pour Contribuer
1. Signer le Contrat de Licence de Contributeur (CLA)
2. Respecter le Code de Conduite Open Source de Microsoft

### Configuration de l'Environnement de Développement
1. **Fork du référentiel** : Créer votre propre fork et cloner localement
2. **Installer les dépendances de développement** :
   ```bash
   python -m pip install -r dev-requirements.txt
   ```
3. **Configurer pre-commit** :
   ```bash
   pre-commit install
   ```

### Outils de Qualité du Code
- **black** : Formatage du code Python
- **nb-clean** : Nettoyage des métadonnées des Jupyter Notebooks
- **ruff** : Vérification du code Python

### Normes de Rédaction des Exemples
- Créer un répertoire séparé pour chaque exemple
- Inclure une documentation README
- Utiliser le modèle Jupyter Notebook pour les exemples Python

---

## 🔒 Sécurité

- Ne signalez pas les vulnérabilités de sécurité via les Issues GitHub publiques
- Signalez les problèmes de sécurité au [Microsoft Security Response Center](https://msrc.microsoft.com/create-report)
- Ou envoyez un e-mail à secure@microsoft.com

---

## 📁 Structure du Référentiel

```
foundry-samples/
├── samples/
│   ├── microsoft/
│   │   ├── python/          # Exemples Python
│   │   ├── javascript/      # Exemples JavaScript
│   │   ├── typescript/      # Exemples TypeScript
│   │   ├── csharp/          # Exemples C#
│   │   ├── java/            # Exemples Java
│   │   ├── REST/            # Exemples API REST
│   │   ├── data/            # Données d'exemple
│   │   └── infrastructure-setup/  # Modèles IaC
│   └── mistral/             # Exemples Mistral AI
├── libs/                    # Bibliothèques précompilées
├── .infra/                  # Fichiers modèles
└── README.md
```

---

## 🔗 Liens Utiles

- [Documentation Officielle Azure AI Foundry](https://learn.microsoft.com/azure/ai-studio/)
- [Navigateur d'Exemples de Code Microsoft](https://docs.microsoft.com/samples)
- [Contrat de Licence de Contributeur (CLA)](https://cla.opensource.microsoft.com)

---

*Ce document a été généré automatiquement par GitHub Copilot, dernière mise à jour : novembre 2025*
