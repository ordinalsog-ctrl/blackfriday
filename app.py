import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st
st.set_page_config(page_title='Black Friday Intelligence | V0.6',layout='wide')
DB=Path(__file__).parent/'blackfriday.sqlite'
st.title('Black Friday Intelligence')
st.caption('Deutschland + EU | Transparenter Preisvergleich | Keine nicht belegten Rabattversprechen')
if not DB.exists():
    st.error('Bitte zuerst `python main.py init` ausführen.'); st.stop()
with sqlite3.connect(DB) as con:
    products=pd.read_sql_query('SELECT * FROM products',con)
    sources=pd.read_sql_query('SELECT name,source_type,access_method,automated_access_approved FROM sources',con)
    observations=pd.read_sql_query('''SELECT o.observation_id,p.candidate_name,p.category,o.observed_at,o.country_code,
       o.item_price_cents,o.shipping_cents,o.availability,o.review_status,o.identity_verified,o.evidence_verified,
       o.source_url FROM price_observations o JOIN products p ON o.product_id=p.product_id
       ORDER BY o.observed_at DESC''',con)
c1,c2,c3,c4=st.columns(4)
c1.metric('Kandidaten',len(products));c2.metric('Identifizierte Artikel',int(products.status.isin(['IDENTIFIED','VALIDATED']).sum()))
c3.metric('Preisbelege in Prüfung',len(observations));c4.metric('Freigegebene Belege',int((observations.review_status=='APPROVED').sum()) if len(observations) else 0)
t1,t2,t3,t4,t5,t6=st.tabs(['Produktstamm','Preisbelege & Quellen','Methodik','Pilot-20 Verifikation','Historienabdeckung','Datenbeschaffung v0.6'])
with t1:
    cat=st.selectbox('Kategorie',['Alle']+sorted(products.category.unique().tolist()))
    q=st.text_input('Suche')
    view=products if cat=='Alle' else products[products.category==cat]
    if q: view=view[view.candidate_name.str.contains(q,case=False,regex=False,na=False)]
    st.dataframe(view,use_container_width=True,hide_index=True)
    st.download_button('Katalog exportieren',view.to_csv(index=False).encode('utf-8-sig'),'katalog.csv','text/csv')
with t2:
    if observations.empty: st.warning('Noch keine in die Datenbank eingespielten historischen Beobachtungen. CSV-Staging und manuelle Quellenprüfung sind erforderlich.')
    else: st.dataframe(observations,use_container_width=True,hide_index=True)
    st.subheader('Datenquellen');st.dataframe(sources,use_container_width=True,hide_index=True)
with t3:
    st.markdown('''**Freigaberegel:** Kein Deal-Score ohne geprüfte Produktidentität, dokumentierte Quelle,
    Endpreis inklusive Versand, Lieferbarkeit und ausreichend historische, unabhängige Beobachtungen.
    90-Tage-Median ist eine Marktkennzahl; der gesetzliche niedrigste Händlerpreis der letzten 30 Tage
    ist eine andere Referenz und darf nicht gleichgesetzt werden.
    **Aktuelle Einschränkung:** Der 500er-Katalog ist eine redaktionelle Kandidatenliste, keine Bestsellerstatistik.''')

with t4:
    st.subheader('20 Pilotprodukte: dokumentierter Prüfstatus')
    st.caption('Ein Quellen-Treffer bestätigt weder EAN noch vollständige Preishistorie. Nicht geprüfte Belege dürfen keine Rabattberechnung auslösen.')
    audit_file=Path(__file__).parent/'data'/'pilot20_verifikationsregister.csv'
    if audit_file.exists():
        audit=pd.read_csv(audit_file,dtype=str).fillna('')
        k1,k2,k3=st.columns(3)
        k1.metric('Pilotartikel',len(audit))
        k2.metric('Quellenseite erneut abgeglichen',int((audit.identity_status!='NOT_RECHECKED').sum()))
        k3.metric('90-Tage-Median belegbar',int((audit['90d_median_eur']!='').sum()))
        st.dataframe(audit,use_container_width=True,hide_index=True)
        st.download_button('Prüfregister exportieren',audit.to_csv(index=False).encode('utf-8-sig'),'pilot20_verifikationsregister.csv','text/csv')
    else: st.info('Prüfregister mit `python build_milestone20.py` erzeugen.')

with t5:
    st.subheader('Historische Preisabdeckung und Freigabe')
    st.caption('Die Abdeckung wird aus tatsächlich eingespielten Datenbankbeobachtungen berechnet. Ein Einzelpreis oder ein Angebots-Snapshot ist keine Preiszeitreihe.')
    from src.coverage import rows as coverage_rows
    coverage = pd.DataFrame(coverage_rows(sqlite3.connect(DB), Path(__file__).parent/'data'/'pilot20_verifikationsregister.csv'))
    d1,d2,d3 = st.columns(3)
    d1.metric('Artikel in Pilotprüfung',len(coverage))
    d2.metric('Verifizierte Preisbelege',int(coverage.approved_price_points.sum()))
    d3.metric('Bereit für historische Analyse',int((coverage.assessment_status=='READY_FOR_EVALUATION').sum()))
    st.dataframe(coverage,use_container_width=True,hide_index=True)
    st.download_button('Abdeckungsbericht exportieren',coverage.to_csv(index=False).encode('utf-8-sig'),'historienabdeckung.csv','text/csv')
    st.warning('Keine automatische Freigabe: Identität, echte historische Quelle und vollständiger Endpreis müssen einzeln geprüft werden. Ein 90-Tage-Median ist erst bei ausreichender Historie zulässig.')

with t6:
    st.subheader("Quellenregister und historische Datenbeschaffung")
    st.caption("Quellenbelege sind keine vollständigen Zeitreihen. Kein automatisches Auslesen externer Webseiten und keine erfundenen Rückblicke.")
    evidence=pd.read_csv(Path(__file__).parent/'data'/'quellenregister_pilot20_v06.csv',dtype=str).fillna('')
    acquisition=pd.read_csv(Path(__file__).parent/'data'/'datenbeschaffung_status_v06.csv')
    v1,v2,v3=st.columns(3)
    v1.metric('Pilotprodukte',len(evidence))
    v2.metric('In v0.6 erneut abgeglichene Quellseiten',int((evidence.source_extraction=='manual_review_of_search_indexed_page').sum()))
    v3.metric('Historisch auswertbare Produkte',int((acquisition.normal_price_ready!='NO').sum()))
    st.dataframe(evidence,use_container_width=True,hide_index=True)
    st.dataframe(acquisition,use_container_width=True,hide_index=True)
    st.download_button('Quellenregister exportieren', evidence.to_csv(index=False).encode('utf-8-sig'),'quellenregister_v06.csv','text/csv')
