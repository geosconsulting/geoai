import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import ipywidgets as widgets
from ipywidgets import interact, fixed
from IPython.display import display, HTML
import folium
from folium.plugins import MarkerCluster
from shapely.geometry import Point, Polygon
import contextily as ctx
from sklearn.neighbors import BallTree
import math

class SimulazioneChiusuraUP:
    def __init__(self, file_up, file_lis, file_banche, file_sezioni_censimento, file_presenze):
        """
        Inizializzazione con i dataset necessari per la simulazione
        
        Parameters:
        -----------
        file_up : str
            Percorso del file contenente i dati degli uffici postali
        file_lis : str
            Percorso del file contenente i dati dei punti LIS
        file_banche : str
            Percorso del file contenente i dati delle banche
        file_sezioni_censimento : str
            Percorso del file contenente i dati delle sezioni di censimento
        file_presenze : str
            Percorso del file contenente i dati delle presenze medie
        """
        self.carica_dati(file_up, file_lis, file_banche, file_sezioni_censimento, file_presenze)
        self.configura_parametri_simulazione()
        
    def carica_dati(self, file_up, file_lis, file_banche, file_sezioni_censimento, file_presenze):
        """
        Carica tutti i dataset necessari
        """
        # Caricamento dati degli uffici postali
        self.df_up = pd.read_csv(file_up)
        # Conversione a geodataframe
        geometry = [Point(xy) for xy in zip(self.df_up['longitude'], self.df_up['latitude'])]
        self.gdf_up = gpd.GeoDataFrame(self.df_up, geometry=geometry, crs="EPSG:4326")
        
        # Caricamento dati dei punti LIS
        self.df_lis = pd.read_csv(file_lis)
        geometry = [Point(xy) for xy in zip(self.df_lis['longitude'], self.df_lis['latitude'])]
        self.gdf_lis = gpd.GeoDataFrame(self.df_lis, geometry=geometry, crs="EPSG:4326")
        
        # Caricamento dati delle banche
        self.df_banche = pd.read_csv(file_banche)
        geometry = [Point(xy) for xy in zip(self.df_banche['longitude'], self.df_banche['latitude'])]
        self.gdf_banche = gpd.GeoDataFrame(self.df_banche, geometry=geometry, crs="EPSG:4326")
        
        # Caricamento delle sezioni di censimento
        self.gdf_sezioni = gpd.read_file(file_sezioni_censimento)
        
        # Caricamento dati di presenze medie
        self.df_presenze = pd.read_csv(file_presenze)
        
        # Preparazione strutture dati per la ricerca spaziale
        self.prepara_balltree()
        
    def prepara_balltree(self):
        """
        Prepara le strutture dati BallTree per ricerche spaziali efficienti
        """
        # Converte coordinate in radianti per BallTree
        def get_spherical_coords(gdf):
            lon = np.radians(gdf.geometry.x)
            lat = np.radians(gdf.geometry.y)
            return np.column_stack([lon, lat])
        
        # Crea BallTree per ogni dataset
        self.up_tree = BallTree(get_spherical_coords(self.gdf_up), metric='haversine')
        self.lis_tree = BallTree(get_spherical_coords(self.gdf_lis), metric='haversine')
        self.banche_tree = BallTree(get_spherical_coords(self.gdf_banche), metric='haversine')
    
    def configura_parametri_simulazione(self):
        """
        Configura i parametri di default per la simulazione
        """
        # Parametri per la distribuzione della produzione
        self.params = {
            # Raggio di influenza in metri - varierà in base alla densità di popolazione
            'raggio_base': 1000,
            
            # Coefficienti di ridistribuzione per servizi disponibili nei LIS
            'servizi_lis': {
                'bollettini': {'up_vicini': 0.4, 'lis_vicini': 0.3, 'competitor': 0.2, 'digitale': 0.1},
                'bollette': {'up_vicini': 0.4, 'lis_vicini': 0.3, 'competitor': 0.2, 'digitale': 0.1},
                'pagoPA': {'up_vicini': 0.4, 'lis_vicini': 0.3, 'competitor': 0.2, 'digitale': 0.1},
                'ricariche_postepay': {'up_vicini': 0.4, 'lis_vicini': 0.3, 'competitor': 0.2, 'digitale': 0.1},
                'ricariche_telefoniche': {'up_vicini': 0.4, 'lis_vicini': 0.3, 'competitor': 0.2, 'digitale': 0.1},
                'pacchi': {'up_vicini': 0.5, 'lis_vicini': 0.2, 'competitor': 0.2, 'digitale': 0.1},
            },
            
            # Coefficienti di ridistribuzione per servizi disponibili solo negli uffici postali
            'servizi_up': {
                'polizze': {'up_vicini': 0.7, 'competitor': 0.2, 'digitale': 0.1},
                'conti': {'up_vicini': 0.7, 'competitor': 0.2, 'digitale': 0.1},
                'fibra': {'up_vicini': 0.6, 'competitor': 0.3, 'digitale': 0.1},
                'energia': {'up_vicini': 0.6, 'competitor': 0.3, 'digitale': 0.1},
                'altri_servizi': {'up_vicini': 0.7, 'competitor': 0.2, 'digitale': 0.1},
            }
        }
    
    def calcola_raggio_ricerca(self, densita_popolazione):
        """
        Calcola il raggio di ricerca in base alla densità della popolazione
        
        Parameters:
        -----------
        densita_popolazione : float
            Densità della popolazione nell'area (abitanti/km²)
            
        Returns:
        --------
        float : raggio di ricerca in metri
        """
        # Raggio inversamente proporzionale alla densità, con limiti
        if densita_popolazione <= 100:  # Zone rurali
            return self.params['raggio_base'] * 3
        elif densita_popolazione <= 1000:  # Zone suburbane
            return self.params['raggio_base'] * 2
        elif densita_popolazione <= 5000:  # Zone urbane
            return self.params['raggio_base']
        else:  # Zone ad alta densità
            return self.params['raggio_base'] * 0.7
    
    def trova_punti_vicini(self, punto_chiusura, raggio_km):
        """
        Trova tutti i punti (UP, LIS, banche) entro un certo raggio
        
        Parameters:
        -----------
        punto_chiusura : Point
            Geometria del punto dell'ufficio postale da chiudere
        raggio_km : float
            Raggio di ricerca in chilometri
            
        Returns:
        --------
        dict : Dizionario contenente i punti vicini per categoria
        """
        # Converti coordinate in radianti
        lon, lat = np.radians([punto_chiusura.x, punto_chiusura.y])
        punto_rad = np.array([[lon, lat]])
        
        # Trova uffici postali vicini (escluso quello da chiudere)
        indici_up = self.up_tree.query_radius(punto_rad, r=raggio_km/6371.0)[0]  # raggio/raggio terra
        up_vicini = self.gdf_up.iloc[indici_up].copy()
        up_vicini = up_vicini[up_vicini.geometry != punto_chiusura]
        
        # Calcola la distanza di ciascun UP vicino e aggiungi come colonna
        up_vicini['distanza_km'] = up_vicini.geometry.apply(
            lambda p: punto_chiusura.distance(p) * 111  # approssimazione km (1 grado ≈ 111 km)
        )
        
        # Trova LIS vicini abilitati
        indici_lis = self.lis_tree.query_radius(punto_rad, r=raggio_km/6371.0)[0]
        lis_vicini = self.gdf_lis.iloc[indici_lis].copy()
        
        # Calcola la distanza di ciascun LIS vicino
        lis_vicini['distanza_km'] = lis_vicini.geometry.apply(
            lambda p: punto_chiusura.distance(p) * 111
        )
        
        # Trova banche vicine
        indici_banche = self.banche_tree.query_radius(punto_rad, r=raggio_km/6371.0)[0]
        banche_vicine = self.gdf_banche.iloc[indici_banche].copy()
        
        # Calcola la distanza di ciascuna banca vicina
        banche_vicine['distanza_km'] = banche_vicine.geometry.apply(
            lambda p: punto_chiusura.distance(p) * 111
        )
        
        return {
            'up_vicini': up_vicini,
            'lis_vicini': lis_vicini,
            'banche_vicine': banche_vicine
        }
    
    def calcola_pesi_distanza(self, punti, distanza_max):
        """
        Calcola pesi inversamente proporzionali alla distanza
        
        Parameters:
        -----------
        punti : GeoDataFrame
            DataFrame contenente i punti con la colonna 'distanza_km'
        distanza_max : float
            Distanza massima considerata in km
            
        Returns:
        --------
        Series : Serie con i pesi calcolati
        """
        if len(punti) == 0:
            return pd.Series()
            
        # Calcola peso come inverso della distanza al quadrato (con limite minimo)
        pesi = 1 / np.maximum(punti['distanza_km']**2, 0.01)
        
        # Normalizza i pesi per sommare a 1
        return pesi / pesi.sum() if pesi.sum() > 0 else pesi
    
    def simula_chiusura_up(self, id_up, personalizza_parametri=None):
        """
        Simula la chiusura di un ufficio postale e calcola la redistribuzione
        
        Parameters:
        -----------
        id_up : str o int
            Identificativo dell'ufficio postale da chiudere
        personalizza_parametri : dict, optional
            Parametri personalizzati per la simulazione
            
        Returns:
        --------
        dict : Risultati della simulazione
        """
        # Aggiorna parametri se necessario
        params = self.params.copy()
        if personalizza_parametri:
            # Aggiorna i parametri in modo ricorsivo
            def update_dict(d, u):
                for k, v in u.items():
                    if isinstance(v, dict):
                        d[k] = update_dict(d.get(k, {}), v)
                    else:
                        d[k] = v
                return d
            params = update_dict(params, personalizza_parametri)
        
        # Trova l'ufficio postale da chiudere
        up_da_chiudere = self.gdf_up[self.gdf_up['id'] == id_up]
        if len(up_da_chiudere) == 0:
            return {'errore': f"Ufficio postale con ID {id_up} non trovato"}
        
        # Ottieni dati dell'ufficio da chiudere
        punto_chiusura = up_da_chiudere.iloc[0].geometry
        produzione_up = up_da_chiudere.iloc[0].to_dict()
        
        # Determina densità popolazione nell'area
        # Cerca la sezione di censimento che contiene il punto
        sezione = self.gdf_sezioni[self.gdf_sezioni.contains(punto_chiusura)]
        if len(sezione) > 0:
            # Calcola densità (abitanti/km²)
            area_km2 = sezione.iloc[0].geometry.area / 1_000_000  # converti m² in km²
            densita = sezione.iloc[0]['popolazione'] / area_km2 if area_km2 > 0 else 1000
        else:
            # Valore di default se non trovata
            densita = 1000
        
        # Calcola raggio di ricerca in base alla densità
        raggio_km = self.calcola_raggio_ricerca(densita) / 1000  # converti metri in km
        
        # Trova punti vicini
        punti_vicini = self.trova_punti_vicini(punto_chiusura, raggio_km)
        
        # Calcola redistribuzione per ogni tipo di servizio
        risultati = {
            'up_chiuso': up_da_chiudere.iloc[0].to_dict(),
            'raggio_km': raggio_km,
            'densita_popolazione': densita,
            'redistribuzione': {},
            'totali': {'up_vicini': {}, 'lis_vicini': {}, 'competitor': {}, 'digitale': {}}
        }
        
        # Calcola pesi basati sulla distanza per UP e LIS
        pesi_up = self.calcola_pesi_distanza(punti_vicini['up_vicini'], raggio_km)
        pesi_lis = self.calcola_pesi_distanza(punti_vicini['lis_vicini'], raggio_km)
        pesi_banche = self.calcola_pesi_distanza(punti_vicini['banche_vicine'], raggio_km)
        
        # Processa servizi disponibili nei LIS
        for servizio, distribuzione in params['servizi_lis'].items():
            if servizio not in produzione_up:
                continue
                
            volume_originale = produzione_up[servizio]
            redistribuzione = {}
            
            # Redistribuzione agli uffici postali vicini
            volume_up = volume_originale * distribuzione['up_vicini']
            redistribuzione_up = {}
            
            for i, (idx, peso) in enumerate(pesi_up.items()):
                up_id = punti_vicini['up_vicini'].iloc[i]['id']
                volume_assegnato = volume_up * peso
                redistribuzione_up[up_id] = volume_assegnato
                
            # Redistribuzione ai LIS vicini (solo se abilitati per quel servizio)
            volume_lis = volume_originale * distribuzione['lis_vicini']
            redistribuzione_lis = {}
            
            # Filtra LIS abilitati per questo servizio
            lis_abilitati = punti_vicini['lis_vicini'][punti_vicini['lis_vicini'][f'abilitato_{servizio}'] == True]
            
            if len(lis_abilitati) > 0:
                # Ricalcola pesi solo per i LIS abilitati
                pesi_lis_abilitati = self.calcola_pesi_distanza(lis_abilitati, raggio_km)
                
                for i, (idx, peso) in enumerate(pesi_lis_abilitati.items()):
                    lis_id = lis_abilitati.iloc[i]['id']
                    volume_assegnato = volume_lis * peso
                    redistribuzione_lis[lis_id] = volume_assegnato
            else:
                # Se non ci sono LIS abilitati, ridistribuisci agli UP
                volume_up += volume_lis
                # Ricalcola redistribuzione UP
                for i, (idx, peso) in enumerate(pesi_up.items()):
                    up_id = punti_vicini['up_vicini'].iloc[i]['id']
                    redistribuzione_up[up_id] = volume_up * peso
            
            # Volume perso a favore dei competitor
            volume_competitor = volume_originale * distribuzione['competitor']
            
            # Volume perso per digitalizzazione
            volume_digitale = volume_originale * distribuzione['digitale']
            
            # Salva risultati per questo servizio
            risultati['redistribuzione'][servizio] = {
                'volume_originale': volume_originale,
                'up_vicini': redistribuzione_up,
                'lis_vicini': redistribuzione_lis,
                'competitor': volume_competitor,
                'digitale': volume_digitale
            }
            
            # Aggiorna totali
            risultati['totali']['up_vicini'][servizio] = sum(redistribuzione_up.values())
            risultati['totali']['lis_vicini'][servizio] = sum(redistribuzione_lis.values())
            risultati['totali']['competitor'][servizio] = volume_competitor
            risultati['totali']['digitale'][servizio] = volume_digitale
        
        # Processa servizi disponibili solo negli UP
        for servizio, distribuzione in params['servizi_up'].items():
            if servizio not in produzione_up:
                continue
                
            volume_originale = produzione_up[servizio]
            redistribuzione = {}
            
            # Redistribuzione agli uffici postali vicini
            volume_up = volume_originale * distribuzione['up_vicini']
            redistribuzione_up = {}
            
            for i, (idx, peso) in enumerate(pesi_up.items()):
                up_id = punti_vicini['up_vicini'].iloc[i]['id']
                volume_assegnato = volume_up * peso
                redistribuzione_up[up_id] = volume_assegnato
            
            # Volume perso a favore dei competitor
            volume_competitor = volume_originale * distribuzione['competitor']
            
            # Volume perso per digitalizzazione
            volume_digitale = volume_originale * distribuzione['digitale']
            
            # Salva risultati per questo servizio
            risultati['redistribuzione'][servizio] = {
                'volume_originale': volume_originale,
                'up_vicini': redistribuzione_up,
                'competitor': volume_competitor,
                'digitale': volume_digitale
            }
            
            # Aggiorna totali
            risultati['totali']['up_vicini'][servizio] = sum(redistribuzione_up.values())
            risultati['totali']['competitor'][servizio] = volume_competitor
            risultati['totali']['digitale'][servizio] = volume_digitale
        
        return risultati
    
    def visualizza_risultati(self, risultati, mostra_mappa=True):
        """
        Visualizza i risultati della simulazione
        
        Parameters:
        -----------
        risultati : dict
            Risultati della simulazione
        mostra_mappa : bool, optional
            Se True, visualizza anche una mappa interattiva
        """
        if 'errore' in risultati:
            return HTML(f"<div style='color: red; font-weight: bold;'>{risultati['errore']}</div>")
        
        # Crea HTML per la visualizzazione dei risultati
        html_output = """
        <div style="padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
            <h2>Risultati Simulazione Chiusura UP</h2>
            
            <div style="margin-bottom: 20px;">
                <h3>Informazioni Ufficio Chiuso</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">ID</th>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{id}</td>
                    </tr>
                    <tr>
                        <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Nome</th>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{nome}</td>
                    </tr>
                    <tr>
                        <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Raggio di ricerca</th>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{raggio_km:.2f} km</td>
                    </tr>
                    <tr>
                        <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Densità popolazione</th>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;">{densita:.2f} ab/km²</td>
                    </tr>
                </table>
            </div>
        """.format(
            id=risultati['up_chiuso']['id'], 
            nome=risultati['up_chiuso'].get('nome', 'N/D'),
            raggio_km=risultati['raggio_km'],
            densita=risultati['densita_popolazione']
        )
        
        # Riepilogo redistribuzione per tipo di servizio
        html_output += """
            <div style="margin-bottom: 20px;">
                <h3>Riepilogo Redistribuzione</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <th style="text-align: left; padding: 8px; border-bottom: 1px solid #ddd;">Servizio</th>
                        <th style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">Volume Originale</th>
                        <th style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">UP Vicini</th>
                        <th style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">LIS Vicini</th>
                        <th style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">Competitor</th>
                        <th style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">Digitale</th>
                    </tr>
        """
        
        # Aggiungi riga per ogni servizio
        for servizio, dati in risultati['redistribuzione'].items():
            volume_originale = dati['volume_originale']
            
            # Calcola volumi redistribuiti
            volume_up = sum(dati['up_vicini'].values()) if 'up_vicini' in dati else 0
            volume_lis = sum(dati['lis_vicini'].values()) if 'lis_vicini' in dati else 0
            volume_competitor = dati['competitor']
            volume_digitale = dati['digitale']
            
            # Formatta come percentuali
            perc_up = (volume_up / volume_originale * 100) if volume_originale > 0 else 0
            perc_lis = (volume_lis / volume_originale * 100) if volume_originale > 0 else 0
            perc_competitor = (volume_competitor / volume_originale * 100) if volume_originale > 0 else 0
            perc_digitale = (volume_digitale / volume_originale * 100) if volume_originale > 0 else 0
            
            html_output += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{servizio}</td>
                    <td style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">{volume_originale:.2f}</td>
                    <td style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">{volume_up:.2f} ({perc_up:.1f}%)</td>
                    <td style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">{volume_lis:.2f} ({perc_lis:.1f}%)</td>
                    <td style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">{volume_competitor:.2f} ({perc_competitor:.1f}%)</td>
                    <td style="text-align: center; padding: 8px; border-bottom: 1px solid #ddd;">{volume_digitale:.2f} ({perc_digitale:.1f}%)</td>
                </tr>
            """
        
        html_output += """
                </table>
            </div>
        </div>
        """
        
        display(HTML(html_output))
        
        # Visualizza grafici
        self.visualizza_grafici_redistribuzione(risultati)
        
        # Visualizza mappa se richiesto
        if mostra_mappa:
            self.visualizza_mappa_redistribuzione(risultati)
    
    def visualizza_grafici_redistribuzione(self, risultati):
        """
        Visualizza grafici della redistribuzione
        
        Parameters:
        -----------
        risultati : dict
            Risultati della simulazione
        """
        # Prepara dati per i grafici
        servizi = list(risultati['redistribuzione'].keys())
        n_servizi = len(servizi)
        
        # Crea subplots
        fig, axs = plt.subplots(1, n_servizi, figsize=(5*n_servizi, 6), sharey=True)
        if n_servizi == 1:
            axs = [axs]
        
        for i, servizio in enumerate(servizi):
            dati = risultati['redistribuzione'][servizio]
            volume_originale = dati['volume_originale']
            
            # Ottieni volumi redistribuiti
            categorie = []
            volumi = []
            colori = []
            
            if 'up_vicini' in dati:
                categorie.append('UP Vicini')
                volumi.append(sum(dati['up_vicini'].values()))
                colori.append('#4CAF50')  # Verde
            
            if 'lis_vicini' in dati:
                categorie.append('LIS Vicini')
                volumi.append(sum(dati['lis_vicini'].values()))
                colori.append('#2196F3')  # Blu
            
            categorie.append('Competitor')
            volumi.append(dati['competitor'])
            colori.append('#F44336')  # Rosso
            
            categorie.append('Digitale')
            volumi.append(dati['digitale'])
            colori.append('#9C27B0')  # Viola
            
            # Crea grafico a barre
            bars = axs[i].bar(categorie, volumi, color=colori)
            
            # Aggiungi percentuali sopra le barre
            for bar in bars:
                height = bar.get_height()
                perc = (height / volume_originale) * 100 if volume_originale > 0 else 0
                axs[i].text(bar.get_x() + bar.get_width()/2., height + 5,
                        f'{perc:.1f}%', ha='center', va='bottom')
            
            # Aggiungi linea orizzontale per il volume originale
            axs[i].axhline(y=volume_originale, color='r', linestyle='-', alpha=0.3)
            axs[i].text(0, volume_originale*1.02, f'Volume originale: {volume_originale:.2f}', 
                     color='r', ha='left', va='bottom')
            
            axs[i].set_title(f'Redistribuzione {servizio}')
            axs[i].set_ylabel('Volume')
            axs[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def visualizza_mappa_redistribuzione(self, risultati):
        """
        Visualizza una mappa interattiva della redistribuzione
        
        Parameters:
        -----------
        risultati : dict
            Risultati della simulazione
        """
        # Estrai le coordinate dell'ufficio chiuso
        up_chiuso = risultati['up_chiuso']
        coord_chiuso = (up_chiuso['latitude'], up_chiuso['longitude'])
        
        # Crea mappa centrata sull'ufficio chiuso
        mappa = folium.Map(location=coord_chiuso, zoom_start=14)
        
        # Aggiungi cerchio di influenza
        folium.Circle(
            location=coord_chiuso,
            radius=risultati['raggio_km'] * 1000,  # converti in metri
            color='red',
            fill=True,
            fill_opacity=0.1,
            popup='Area di influenza'
        ).add_to(mappa)
        
        # Aggiungi marker per l'ufficio chiuso
        folium.Marker(
            location=coord_chiuso,
            icon=folium.Icon(color='red', icon='times', prefix='fa'),
            popup=f"UP CHIUSO: {up_chiuso.get('nome', 'N/D')}"
        ).add_to(mappa)
        
        # Aggiungi marker per gli uffici postali vicini che ricevono redistribuzione
        up_riceventi = {}
        for servizio, dati in risultati['redistribuzione'].items():
            if 'up_vicini' not in dati:
                continue
                
            for up_id, volume in dati['up_vicini'].items():
                if up_id not in up_riceventi:
                    up_riceventi[up_id] = {'totale': 0, 'servizi': {}}
                
                up_riceventi[up_id]['totale'] += volume
                up_riceventi[up_id]['servizi'][servizio] = volume
        
        # Aggiungi marker per UP riceventi
        for up_id, dati in up_riceventi.items():
            # Trova l'UP nel dataframe originale
            up_info = self.df_up[self.df_up['id'] == up_id]
            if len(up_info) == 0:
                continue
                
            up_row = up_info.iloc[0]
            
            # Crea popup con informazioni dettagliate
            popup_html = f"""
            <div style="min-width: 200px;">
                <h4>{up_row.get('nome', f'UP {up_id}')}</h4>
                <p><strong>Volume totale ricevuto:</strong> {dati['totale']:.2f}</p>
                <table style="width: 100%;">
                    <tr>
                        <th style="text-align: left;">Servizio</th>
                        <th style="text-align: right;">Volume</th>
                    </tr>
            """
            
            for servizio, volume in dati['servizi'].items():
                popup_html += f"""
                    <tr>
                        <td>{servizio}</td>
                        <td style="text-align: right;">{volume:.2f}</td>
                    </tr>
                """
            
            popup_html += """
                </table>
            </div>
            """
            
            # Aggiungi marker
            folium.Marker(
                location=(up_row['latitude'], up_row['longitude']),
                icon=folium.Icon(color='green', icon='envelope', prefix='fa'),
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(mappa)
        
        # Aggiungi marker per i LIS vicini che ricevono redistribuzione
        lis_riceventi = {}
        for servizio, dati in risultati['redistribuzione'].items():
            if 'lis_vicini' not in dati:
                continue
                
            for lis_id, volume in dati['lis_vicini'].items():
                if lis_id not in lis_riceventi:
                    lis_riceventi[lis_id] = {'totale': 0, 'servizi': {}}
                
                lis_riceventi[lis_id]['totale'] += volume
                lis_riceventi[lis_id]['servizi'][servizio] = volume
        
        # Aggiungi marker per LIS riceventi
        for lis_id, dati in lis_riceventi.items():
            # Trova il LIS nel dataframe originale
            lis_info = self.df_lis[self.df_lis['id'] == lis_id]
            if len(lis_info) == 0:
                continue
                
            lis_row = lis_info.iloc[0]
            
            # Crea popup con informazioni dettagliate
            popup_html = f"""
            <div style="min-width: 200px;">
                <h4>{lis_row.get('nome', f'LIS {lis_id}')}</h4>
                <p><strong>Volume totale ricevuto:</strong> {dati['totale']:.2f}</p>
                <table style="width: 100%;">
                    <tr>
                        <th style="text-align: left;">Servizio</th>
                        <th style="text-align: right;">Volume</th>
                    </tr>
            """
            
            for servizio, volume in dati['servizi'].items():
                popup_html += f"""
                    <tr>
                        <td>{servizio}</td>
                        <td style="text-align: right;">{volume:.2f}</td>
                    </tr>
                """
            
            popup_html += """
                </table>
            </div>
            """
            
            # Aggiungi marker
            folium.Marker(
                location=(lis_row['latitude'], lis_row['longitude']),
                icon=folium.Icon(color='blue', icon='shopping-basket', prefix='fa'),
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(mappa)
        
        # Aggiungi marker per le banche competitor
        marker_cluster = MarkerCluster().add_to(mappa)
        
        # Cerca banche nel raggio di influenza
        punto_chiuso = Point(up_chiuso['longitude'], up_chiuso['latitude'])
        banche_nel_raggio = self.gdf_banche[self.gdf_banche.geometry.apply(
            lambda p: p.distance(punto_chiuso) * 111 <= risultati['raggio_km']
        )]
        
        for idx, banca in banche_nel_raggio.iterrows():
            folium.Marker(
                location=(banca['latitude'], banca['longitude']),
                icon=folium.Icon(color='purple', icon='university', prefix='fa'),
                popup=f"Banca: {banca.get('nome', 'N/D')}<br>Gruppo: {banca.get('gruppo', 'N/D')}"
            ).add_to(marker_cluster)
        
        # Aggiungi legenda
        legenda_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
            <p><i class="fa fa-times fa-1x" style="color:red"></i> UP Chiuso</p>
            <p><i class="fa fa-envelope fa-1x" style="color:green"></i> UP Riceventi</p>
            <p><i class="fa fa-shopping-basket fa-1x" style="color:blue"></i> LIS Riceventi</p>
            <p><i class="fa fa-university fa-1x" style="color:purple"></i> Banche competitor</p>
            <p style="color:red; opacity: 0.5;">⬤</p> Area di influenza
        </div>
        """
        mappa.get_root().html.add_child(folium.Element(legenda_html))
        
        # Mostra la mappa
        return mappa
    
    def crea_interfaccia_simulazione(self):
        """
        Crea un'interfaccia interattiva per la simulazione
        
        Returns:
        --------
        widget : ipywidgets.Widget
            Widget interattivo per la simulazione
        """
        # Crea dropdown per la selezione dell'ufficio postale
        options_up = [(f"{row['id']} - {row.get('nome', 'N/D')}", row['id']) for _, row in self.df_up.iterrows()]
        dropdown_up = widgets.Dropdown(
            options=options_up,
            description='Ufficio Postale:',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='50%')
        )
        
        # Slider per i parametri di redistribuzione
        sliders_servizi_lis = {}
        for servizio in ['bollettini', 'bollette', 'pagoPA', 'ricariche_postepay', 'ricariche_telefoniche', 'pacchi']:
            sliders_servizi_lis[servizio] = {
                'up': widgets.FloatSlider(
                    value=self.params['servizi_lis'][servizio]['up_vicini'],
                    min=0, max=1, step=0.05,
                    description=f'UP ({servizio}):',
                    style={'description_width': 'initial'},
                    layout=widgets.Layout(width='90%')
                ),
                'lis': widgets.FloatSlider(
                    value=self.params['servizi_lis'][servizio]['lis_vicini'],
                    min=0, max=1, step=0.05,
                    description=f'LIS ({servizio}):',
                    style={'description_width': 'initial'},
                    layout=widgets.Layout(width='90%')
                ),
                'competitor': widgets.FloatSlider(
                    value=self.params['servizi_lis'][servizio]['competitor'],
                    min=0, max=1, step=0.05,
                    description=f'Competitor ({servizio}):',
                    style={'description_width': 'initial'},
                    layout=widgets.Layout(width='90%')
                ),
                'digitale': widgets.FloatSlider(
                    value=self.params['servizi_lis'][servizio]['digitale'],
                    min=0, max=1, step=0.05,
                    description=f'Digitale ({servizio}):',
                    style={'description_width': 'initial'},
                    layout=widgets.Layout(width='90%')
                )
            }
        
        sliders_servizi_up = {}
        for servizio in ['polizze', 'conti', 'fibra', 'energia', 'altri_servizi']:
            sliders_servizi_up[servizio] = {
                'up': widgets.FloatSlider(
                    value=self.params['servizi_up'][servizio]['up_vicini'],
                    min=0, max=1, step=0.05,
                    description=f'UP ({servizio}):',
                    style={'description_width': 'initial'},
                    layout=widgets.Layout(width='90%')
                ),
                'competitor': widgets.FloatSlider(
                    value=self.params['servizi_up'][servizio]['competitor'],
                    min=0, max=1, step=0.05,
                    description=f'Competitor ({servizio}):',
                    style={'description_width': 'initial'},
                    layout=widgets.Layout(width='90%')
                ),
                'digitale': widgets.FloatSlider(
                    value=self.params['servizi_up'][servizio]['digitale'],
                    min=0, max=1, step=0.05,
                    description=f'Digitale ({servizio}):',
                    style={'description_width': 'initial'},
                    layout=widgets.Layout(width='90%')
                )
            }
        
        # Slider per il raggio base
        slider_raggio = widgets.FloatSlider(
            value=self.params['raggio_base'],
            min=500, max=5000, step=100,
            description='Raggio base (m):',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='50%')
        )
        
        # Checkbox per mostrare la mappa
        checkbox_mappa = widgets.Checkbox(
            value=True,
            description='Mostra mappa',
            layout=widgets.Layout(width='auto')
        )
        
        # Bottone per eseguire la simulazione
        button_simula = widgets.Button(
            description='Esegui Simulazione',
            button_style='success',
            layout=widgets.Layout(width='auto')
        )
        
        # Output widget per mostrare i risultati
        output = widgets.Output()
        
        # Creazione dei tab per i parametri
        tab_servizi_lis = []
        for servizio in ['bollettini', 'bollette', 'pagoPA', 'ricariche_postepay', 'ricariche_telefoniche', 'pacchi']:
            box = widgets.VBox([
                sliders_servizi_lis[servizio]['up'],
                sliders_servizi_lis[servizio]['lis'],
                sliders_servizi_lis[servizio]['competitor'],
                sliders_servizi_lis[servizio]['digitale']
            ])
            tab_servizi_lis.append(box)
        
        tab_servizi_up = []
        for servizio in ['polizze', 'conti', 'fibra', 'energia', 'altri_servizi']:
            box = widgets.VBox([
                sliders_servizi_up[servizio]['up'],
                sliders_servizi_up[servizio]['competitor'],
                sliders_servizi_up[servizio]['digitale']
            ])
            tab_servizi_up.append(box)
        
        # Crea tabs per i parametri LIS
        tabs_lis = widgets.Tab()
        tabs_lis.children = tab_servizi_lis
        for i, servizio in enumerate(['bollettini', 'bollette', 'pagoPA', 'ricariche_postepay', 'ricariche_telefoniche', 'pacchi']):
            tabs_lis.set_title(i, servizio)
        
        # Crea tabs per i parametri UP
        tabs_up = widgets.Tab()
        tabs_up.children = tab_servizi_up
        for i, servizio in enumerate(['polizze', 'conti', 'fibra', 'energia', 'altri_servizi']):
            tabs_up.set_title(i, servizio)
        
        # Tabs principale per separare parametri LIS e UP
        tabs_principale = widgets.Tab()
        tabs_principale.children = [tabs_lis, tabs_up]
        tabs_principale.set_title(0, 'Servizi LIS')
        tabs_principale.set_title(1, '