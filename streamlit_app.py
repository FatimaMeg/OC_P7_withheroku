# =========================================
# Dashboard pour l'octroi de crédits bancaires
# Author: Fatima Meguellati
# Last Modified: 08 Aout 2022
# =========================================
# Command to execute script locally: streamlit run app.py



import joblib
import streamlit as st
from lime import lime_tabular
import streamlit.components.v1 as components
import pickle
import matplotlib.pyplot as plt
import requests

# On récupère notre fichier clients pour obtenir les informations descriptives des clients
file_clients_descr = open("application_test.pkl", "rb") #fichier client avec les noms de colonne
donnees_clients_descr = pickle.load(file_clients_descr)
file_clients_descr.close()

#url = 'https://ocp7apicredit.herokuapp.com'

# Set FastAPI endpoints : un pour les prédictions, un autre pour les explications
# endpoint = 'http://127.0.0.1:8000/predict'
endpoint = 'https://ocp7apicredit.herokuapp.com/predict' # Specify this path for Heroku deployment

# endpoint_lime = 'http://127.0.0.1:8000/lime'
endpoint_lime = 'https://ocp7apicredit.herokuapp.com/lime' # Specify this path for Heroku deployment

#endpoint_client = 'http://127.0.0.1:8000/client'
endpoint_client = 'https://ocp7apicredit.herokuapp.com/client' # Specify this path for Heroku deployment

# endpoint_client_data = 'http://127.0.0.1:8000/clientdata'
endpoint_client_data = 'https://ocp7apicredit.herokuapp.com/clientdata' # Specify this path for Heroku deployment

endpoint_client_graph = 'http://127.0.0.1:8000/graphs'
#endpoint_client_data = 'https://ocp7apicredit.herokuapp.com/clientdata' # Specify this path for Heroku deployment

# Mise en page de l'application streamlit
st.set_page_config(
    page_title="Dashboard",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        #'Get Help': 'https://www.extremelycoolapp.com/help',
        #'Report a bug': "https://www.extremelycoolapp.com/bug",
        #'About': "# This is a header. This is an *extremely* cool app!"
    }
)

tab1, tab2, tab3= st.tabs(["Prévision", "Client", "Onglet tests"])

with tab1:
    st.header('Dashboard pour l\'octroi de crédits bancaires')

    with st.sidebar:
        NUM_CLIENT = st.number_input("Numéro du client", min_value=0,
                                    help="Entrez le numéro de client de la base de données clients")

        client_json = {'num_client': NUM_CLIENT}

        client_valide = requests.post(endpoint_client, json=client_json,
                                    timeout=8000)

        attributs_client = ['CODE_GENDER', 'AMT_INCOME_TOTAL',
                            'AMT_CREDIT','DAYS_BIRTH']

        if client_valide.json()[0]:
            choix_attributs = st.multiselect("Sélectionnez les attributs du client à afficher", attributs_client)
            #info_client = donnees_clients_descr.loc[donnees_clients_descr['SK_ID_CURR'] == NUM_CLIENT, choix_attributs]
            
            obtain_pred = st.button('Cliquer ici pour connaitre la décision d\'accorder le prêt ou non')
        else:
            st.warning(
                "Veuillez entrer un numéro de client valide pour obtenir des informations concernant la demande d'octroi de prêt")
            obtain_pred = st.button('Cliquer ici pour connaitre la décision d\'accorder le prêt ou non', disabled=True)

    #Lorsqu'on clique sur le bouton on obtient les prédictions
    if obtain_pred:
        

        with st.spinner('Prediction in Progress. Please Wait...'):
            previsions = requests.post(endpoint_predict, json=client_json, timeout=8000)

        #1er bloc qui contient les résultats de la prévision et données descriptives du client
        container_prev = st.empty()
        with container_prev.container():
            #On créé deux colonnes, une avec le résultat prévision et l'autre avec données descriptives
            col1, col2 = st.columns([1, 4], gap="medium")

            #1ere colonne avec résultats prévisions
            with col1:
                if previsions.json()[0] == 0:
                    indicateur_pret = 'green'
                    message="Bravo, votre demande de crédit peut être acceptée"
                else:
                    indicateur_pret = 'red'
                    message="Malheureusement, votre demande de crédit ne peut être acceptée"

                #Affichage du cercle rouge ou vert en fonction de la prevision
                fig, ax = plt.subplots()
                ax.set(xlim=(-0.1, 0.1), ylim=(-0.1, 0.1))
                a_circle = plt.Circle((0, 0), 0.1, facecolor=indicateur_pret)
                ax.add_artist(a_circle)
                plt.axis('off')
                plt.grid(b=None)
                st.pyplot(fig)
                
                #Affichage message demande de crédit acceptée ou non
                st.write(message)

            
            #2ème colonne avec données descriptives
            with col2:
                st.write("La probabilité de faillite du client est de ", previsions.json()[1])

                #On récupère les données via une requête au format JSON, et on remet sous format Dataframe
                donnees_clients = requests.post(endpoint_client_data, json=client_json, timeout=8000)
                info_client = pd.read_json(donnees_clients.json()[0], orient='records')
                
                # on n'affiche que les attributs sélectionnés dans le sidebar
                info_client_choixattributs = info_client.loc[:, choix_attributs]
                st.dataframe(info_client_choixattributs)



    container_explain = st.empty()
    with container_explain.expander("Cliquez ici pour obtenir des explications concernant cette décision"):
        with st.spinner('Veuillez patienter, nous récupérons des données supplémentaires pour expliquer la décision...'):
            output_lime = requests.post(endpoint_lime, json=client_json, timeout=8000)
        import streamlit.components.v1 as components
        components.html(output_lime.json()[0], height=200)