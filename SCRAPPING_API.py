import streamlit as st
import pandas as pd
import requests
import time

def scrape_google_jobs(query, location, api_key, max_results=100):
    """Scrape Google Jobs avec pagination via next_page_token"""
    all_results = []
    next_page_token = None  # Initialisation du token de pagination

    while len(all_results) < max_results:
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": location,
            "api_key": api_key,
        }

        # Ajouter le token de pagination s'il existe
        if next_page_token:
            params["next_page_token"] = next_page_token

        response = requests.get("https://serpapi.com/search", params=params)

        if response.status_code == 200:
            jobs_data = response.json()

            if "jobs_results" in jobs_data:
                results = jobs_data["jobs_results"]
                all_results.extend(results)
                st.write(f"📄 Scraping page {len(all_results)//10 + 1}...")

                # Vérifier si un token de page suivante est présent
                next_page_token = jobs_data.get("serpapi_pagination", {}).get("next_page_token")

                if not next_page_token:  # Si pas de page suivante, arrêter
                    st.warning("⚠️ Plus de pages disponibles, arrêt du scraping.")
                    break

                time.sleep(2)  # Pause pour éviter les limitations API

            else:
                st.warning("⚠️ Aucune offre trouvée sur cette page.")
                break

        else:
            st.error(f"⚠️ Erreur {response.status_code} : {response.text}")
            break

    return all_results

def main():
    st.title("🔍 Outil de Scraping d'Offres d'Emploi Google Jobs")
    st.markdown("### Récupérez les offres d'emploi de Google Jobs en temps réel.")

    # Saisie des paramètres par l'utilisateur
    query = st.text_input("Entrez le poste recherché (ex: Data Scientist) :", "Data Scientist")
    location = st.text_input("Entrez la localisation (ex: France) :", "France")
    api_key = st.text_input("Entrez votre clé API :", "cee45e2ee3864a8c17953e65972552cf2ebe4edd65e40cab994f7f314afdd27f")
    max_results = st.number_input("Entrez le nombre maximum de résultats à récupérer (ex: 100) :", min_value=1, value=100)

    if st.button("Lancer le Scraping"):
        with st.spinner("Scraping en cours..."):
            results = scrape_google_jobs(query, location, api_key, max_results)

        if results:
            df = pd.DataFrame(results)
            st.success("✅ Données chargées avec succès !")
            
            # Affichage du DataFrame dans un tableau interactif
            st.write("### Résultats des Offres d'Emploi")
            st.dataframe(df)

            # Téléchargement des résultats en Excel
            st.write("### Télécharger les Résultats")
            st.download_button(
                label="Télécharger en Excel",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='google_jobs_results.csv',
                mime='text/csv',
            )
        else:
            st.warning("⚠️ Aucun résultat trouvé.")

if __name__ == "__main__":
    main()
