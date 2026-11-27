"""Dashboard BigData Commerce Analytics (TP3).

Lit les datasets pseudonymisés produits par notebooks/TP3.ipynb.
Lancement, depuis la racine du projet :  python -m streamlit run dashboard/app.py
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DOSSIER_DATA = Path(__file__).resolve().parents[1] / "data" / "analytique"
FICHIER_COMMANDES = DOSSIER_DATA / "commandes_pseudo.parquet"
FICHIER_PAIEMENTS = DOSSIER_DATA / "paiements_pseudo.parquet"

# Une teinte principale pour les séries simples, des couleurs de statut réservées aux paiements
BLEU = "#257de0"
GRIS_TEXTE = "#666666"
STATUTS = {
    "PAID": {"couleur": "#0aac23", "libelle": "Accepté"},
    "PENDING": {"couleur": "#fbb315", "libelle": "En attente"},
    "REFUSED": {"couleur": "#dc3c3d", "libelle": "Refusé"},
}
MOIS_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]

st.set_page_config(page_title="BigData Commerce Analytics", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
      .block-container {padding-top: 3.5rem; max-width: 1300px;}
      h1, h2, h3 {letter-spacing: -0.02em;}
      .entete {display: flex; justify-content: space-between; align-items: flex-end;
               flex-wrap: wrap; gap: 1rem; margin-bottom: 1.2rem;}
      .entete h1 {font-size: 2rem; margin: 0; padding: 0;}
      .entete p {color: #666; margin: .2rem 0 0 0;}
      .badges span {display: inline-block; font-size: .75rem; font-weight: 600; padding: .3rem .7rem;
                    border-radius: 999px; background: #e8f1fc; color: #1b64be; margin-left: .4rem;}
      .kpis {display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; margin: .5rem 0 1.5rem;}
      .kpi {background: #fff; border: 1px solid #e6e9ef; border-radius: 16px; padding: 1.1rem 1.2rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, .04);}
      .kpi .label {font-size: .8rem; color: #666; font-weight: 500; text-transform: uppercase; letter-spacing: .04em;}
      .kpi .valeur {font-size: 1.75rem; font-weight: 700; color: #191919; margin-top: .35rem;}
      .kpi .detail {font-size: .82rem; color: #666; margin-top: .25rem;}
      @media (max-width: 900px) {.kpis {grid-template-columns: repeat(2, minmax(0, 1fr));}}
      div[data-testid="stTabs"] button p {font-size: .95rem; font-weight: 600;}
      .note {font-size: .82rem; color: #666;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------ fonctions utilitaires
def euros(valeur, decimales=0):
    texte = f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")
    return f"{texte} €"


def euros_court(valeur):
    if abs(valeur) >= 1_000_000:
        return f"{valeur / 1_000_000:.2f} M€".replace(".", ",")
    if abs(valeur) >= 1_000:
        return f"{valeur / 1_000:.0f} k€"
    return euros(valeur)


def pourcent(valeur):
    return f"{valeur:.1f} %".replace(".", ",")


def mise_en_forme(fig, hauteur=420):
    """Style commun : fond transparent, grille discrète, nombres à la française, pas de légende (une seule série)."""
    fig.update_layout(
        height=hauteur,
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#191919"),
        margin=dict(l=10, r=20, t=50, b=10),
        separators=", ",
        hoverlabel=dict(bgcolor="white", font_size=13, bordercolor="#e6e9ef"),
        showlegend=False,
        barcornerradius=4,
    )
    fig.update_xaxes(gridcolor="#eef0f4", zeroline=False, linecolor="#d0d5dd", title_font=dict(color=GRIS_TEXTE))
    fig.update_yaxes(gridcolor="#eef0f4", zeroline=False, linecolor="#d0d5dd", title_font=dict(color=GRIS_TEXTE))
    return fig


def axe_euros(axe):
    """Graduations en euros abrégées : 200 k€, 1,5 M€..."""
    axe.update(tickformat="~s", ticksuffix=" €")


def carte_kpi(label, valeur, detail):
    return (f'<div class="kpi"><div class="label">{label}</div>'
            f'<div class="valeur">{valeur}</div><div class="detail">{detail}</div></div>')


def note(texte):
    st.markdown(f'<p class="note">{texte}</p>', unsafe_allow_html=True)


@st.cache_data
def charger_donnees():
    commandes = pd.read_parquet(FICHIER_COMMANDES)
    paiements = pd.read_parquet(FICHIER_PAIEMENTS)
    commandes["order_date"] = pd.to_datetime(commandes["order_date"], errors="coerce")
    paiements["payment_date"] = pd.to_datetime(paiements["payment_date"], errors="coerce")
    paiements["mois"] = paiements["payment_date"].dt.to_period("M").dt.to_timestamp()
    paiements["statut"] = paiements["payment_status"].map(lambda s: STATUTS[s]["libelle"])
    return commandes, paiements


# ------------------------------------------------------------------ données
if not (FICHIER_COMMANDES.exists() and FICHIER_PAIEMENTS.exists()):
    st.error("Datasets introuvables dans data/analytique/. Exécuter d'abord le notebook notebooks/TP3.ipynb.")
    st.stop()

commandes, paiements = charger_donnees()

# ------------------------------------------------------------------ barre latérale : filtres
with st.sidebar:
    st.markdown("### Filtres")
    categories = sorted(commandes["category"].unique())
    choix_categories = st.multiselect("Catégories", categories, default=[],
                                      placeholder="Toutes les catégories")
    if not choix_categories:
        choix_categories = categories
    else:
        st.info("Filtre actif : les montants ne comptent que les produits des catégories choisies, "
                "les nombres de paiements comptent les paniers qui en contiennent au moins un.")
    st.divider()
    note("Données DummyJSON simulées, montants affichés en euros sans conversion. "
         "Les clients sont identifiés uniquement par un pseudonyme HMAC-SHA256 : aucun identifiant direct "
         "n'est présent dans les datasets.")

# Les montants sont calculés au niveau des lignes de produits, pour ne compter que les catégories filtrées.
# Sans filtre, la somme des lignes d'un panier est égale au montant de son paiement.
commandes_f = commandes[commandes["category"].isin(choix_categories)]
lignes_f = commandes_f.merge(
    paiements[["cart_id", "payment_id", "payment_status", "statut", "mois"]], on="cart_id", how="inner"
)
lignes_paid = lignes_f[lignes_f["payment_status"] == "PAID"]
paiements_f = paiements[paiements["cart_id"].isin(commandes_f["cart_id"].unique())]

# ------------------------------------------------------------------ en-tête
st.markdown(
    """
    <div class="entete">
      <div>
        <h1>BigData Commerce Analytics</h1>
        <p>Commandes, paiements et clients de la boutique de démonstration</p>
      </div>
      <div class="badges"><span>MongoDB → PySpark → Parquet</span><span>Clients pseudonymisés</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

onglet_resume, onglet_cat, onglet_mois, onglet_clients, onglet_explo = st.tabs(
    ["Vue d'ensemble", "Catégories", "Évolution mensuelle", "Clients", "Exploration"]
)

# ------------------------------------------------------------------ vue d'ensemble
with onglet_resume:
    ca_commandes = lignes_f["discounted_line_total"].sum()
    encaisse = lignes_paid["discounted_line_total"].sum()
    nb_paniers = commandes_f["cart_id"].nunique()
    nb_paid = lignes_paid["cart_id"].nunique()
    taux_paid = nb_paid / len(paiements_f) * 100 if len(paiements_f) else 0
    part_encaisse = encaisse / ca_commandes * 100 if ca_commandes else 0

    st.markdown(
        '<div class="kpis">'
        + carte_kpi("CA des commandes", euros_court(ca_commandes), "Somme des lignes après remise")
        + carte_kpi("Encaissements", euros_court(encaisse), f"{pourcent(part_encaisse)} du CA des commandes")
        + carte_kpi("Paniers", f"{nb_paniers}", f"{len(commandes_f)} lignes de produits")
        + carte_kpi("Paiements acceptés", pourcent(taux_paid), f"{nb_paid} sur {len(paiements_f)} tentatives")
        + "</div>",
        unsafe_allow_html=True,
    )

    statuts = (
        lignes_f.groupby(["payment_status", "statut"])
        .agg(nb=("cart_id", "nunique"), montant=("discounted_line_total", "sum"))
        .reset_index()
    )
    statuts["part"] = statuts["nb"] / statuts["nb"].sum() * 100
    statuts["ordre"] = statuts["payment_status"].map({"PAID": 0, "PENDING": 1, "REFUSED": 2})
    statuts = statuts.sort_values("ordre", ascending=False)
    couleurs = [STATUTS[s]["couleur"] for s in statuts["payment_status"]]

    col1, col2 = st.columns(2, gap="large")
    with col1, st.container(border=True):
        fig = go.Figure(go.Bar(
            x=statuts["nb"], y=statuts["statut"], orientation="h", marker_color=couleurs,
            text=[f"{n} · {pourcent(p)}" for n, p in zip(statuts["nb"], statuts["part"])],
            textposition="outside", cliponaxis=False,
            hovertemplate="%{y} : %{x} paiements<extra></extra>",
        ))
        fig.update_layout(title="Tentatives de paiement par statut")
        fig.update_xaxes(title="Nombre de paiements", range=[0, statuts["nb"].max() * 1.25])
        st.plotly_chart(mise_en_forme(fig, 320), width="stretch")
    with col2, st.container(border=True):
        fig = go.Figure(go.Bar(
            x=statuts["montant"], y=statuts["statut"], orientation="h", marker_color=couleurs,
            text=[euros_court(m) for m in statuts["montant"]], textposition="outside", cliponaxis=False,
            hovertemplate="%{y} : %{x:,.0f} €<extra></extra>",
        ))
        fig.update_layout(title="Montant associé à chaque statut")
        fig.update_xaxes(title="Montant", range=[0, statuts["montant"].max() * 1.25])
        axe_euros(fig.layout.xaxis)
        st.plotly_chart(mise_en_forme(fig, 320), width="stretch")

    note(f"Seuls les paiements acceptés sont encaissés : {euros(ca_commandes - encaisse)} "
         "de commandes refusées ou en attente ne rapportent rien dans ce scénario.")

# ------------------------------------------------------------------ catégories
with onglet_cat:
    ca_cat = (
        commandes_f.groupby("category")
        .agg(ca=("discounted_line_total", "sum"), articles=("quantity", "sum"))
        .reset_index()
        .sort_values("ca")
    )
    ca_cat["part"] = ca_cat["ca"] / ca_cat["ca"].sum() * 100
    top4 = ca_cat.sort_values("ca", ascending=False).head(4)

    with st.container(border=True):
        fig = go.Figure(go.Bar(
            x=ca_cat["ca"], y=ca_cat["category"], orientation="h", marker_color=BLEU,
            text=[pourcent(p) for p in ca_cat["part"]], textposition="outside", cliponaxis=False,
            customdata=ca_cat[["articles", "part"]],
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} €<br>%{customdata[0]} articles · %{customdata[1]:.1f} %<extra></extra>",
        ))
        fig.update_layout(title="Chiffre d'affaires par catégorie (somme des lignes après remise)")
        fig.update_xaxes(title="Chiffre d'affaires", range=[0, ca_cat["ca"].max() * 1.15])
        axe_euros(fig.layout.xaxis)
        st.plotly_chart(mise_en_forme(fig, max(420, 26 * len(ca_cat))), width="stretch")

    note(f"Les {len(top4)} premières catégories ({', '.join(top4['category'])}) représentent "
         f"{pourcent(top4['part'].sum())} du chiffre d'affaires : il dépend surtout de quelques produits très chers.")

# ------------------------------------------------------------------ évolution mensuelle
with onglet_mois:
    mensuel = (
        lignes_paid.groupby("mois")
        .agg(encaissements=("discounted_line_total", "sum"), nb=("cart_id", "nunique"))
        .reset_index()
        .sort_values("mois")
    )
    mensuel["libelle"] = [f"{MOIS_FR[d.month - 1]} {d.year}" for d in mensuel["mois"]]

    with st.container(border=True):
        fig = go.Figure(go.Scatter(
            x=mensuel["libelle"], y=mensuel["encaissements"], mode="lines+markers",
            line=dict(color=BLEU, width=2), marker=dict(size=8, color=BLEU, line=dict(color="white", width=2)),
            fill="tozeroy", fillcolor="rgba(37,125,224,0.08)",
            customdata=mensuel["nb"],
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} €<br>%{customdata} paiements<extra></extra>",
        ))
        fig.update_layout(title="Encaissements par mois (paiements acceptés)", hovermode="x")
        fig.update_yaxes(title="Montant encaissé", rangemode="tozero")
        axe_euros(fig.layout.yaxis)
        st.plotly_chart(mise_en_forme(fig), width="stretch")

    with st.container(border=True):
        fig = go.Figure(go.Bar(
            x=mensuel["libelle"], y=mensuel["nb"], marker_color=BLEU,
            hovertemplate="<b>%{x}</b><br>%{y} paiements<extra></extra>",
        ))
        fig.update_layout(title="Nombre de paiements acceptés par mois")
        fig.update_yaxes(title="Paiements")
        st.plotly_chart(mise_en_forme(fig, 300), width="stretch")

    note("Le nombre de paiements varie peu alors que les montants varient beaucoup : quelques paniers très chers "
         "font les pics. Les dates sont générées pour l'exercice, pas de conclusion sur une saisonnalité réelle.")

# ------------------------------------------------------------------ clients
with onglet_clients:
    encaisse_total = lignes_paid["discounted_line_total"].sum()
    n = st.slider("Nombre de clients affichés", min_value=5, max_value=30, value=10)
    top = (
        lignes_paid.groupby("user_id_pseudo")["discounted_line_total"].sum()
        .nlargest(n).sort_values().rename("amount").reset_index()
    )
    part = top["amount"].sum() / encaisse_total * 100 if encaisse_total else 0

    with st.container(border=True):
        fig = go.Figure(go.Bar(
            x=top["amount"], y=top["user_id_pseudo"], orientation="h", marker_color=BLEU,
            text=[euros_court(m) for m in top["amount"]], textposition="outside", cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} €<extra></extra>",
        ))
        fig.update_layout(title=f"Top {len(top)} des clients par montant encaissé")
        fig.update_xaxes(title="Montant payé", range=[0, top["amount"].max() * 1.18 if len(top) else 1])
        axe_euros(fig.layout.xaxis)
        fig.update_yaxes(title="Client (pseudonyme)", tickfont=dict(family="Consolas, monospace", size=12))
        st.plotly_chart(mise_en_forme(fig, max(380, 30 * len(top))), width="stretch")

    note(f"Le top {len(top)} représente {pourcent(part)} des encaissements. Chaque client n'a qu'un panier "
         "dans les données : c'est aussi le classement des paniers payés les plus chers.")

# ------------------------------------------------------------------ exploration
with onglet_explo:
    c1, c2 = st.columns([2, 1])
    statuts_choisis = c1.multiselect(
        "Statut de paiement", list(STATUTS), default=list(STATUTS),
        format_func=lambda s: STATUTS[s]["libelle"],
    )
    table = c2.radio("Table", ["Paiements", "Lignes de commandes"], horizontal=True)

    paiements_statut = paiements_f[paiements_f["payment_status"].isin(statuts_choisis)]
    if table == "Paiements":
        donnees = paiements_statut[["payment_id", "cart_id", "user_id_pseudo", "statut", "amount",
                                    "amount_collected", "payment_date", "nb_lignes", "nb_articles"]]
        colonnes = {
            "payment_id": "Paiement", "cart_id": "Panier", "user_id_pseudo": "Client (pseudonyme)",
            "statut": "Statut", "nb_lignes": "Lignes", "nb_articles": "Articles",
            "amount": st.column_config.NumberColumn("Montant", format="%.2f €"),
            "amount_collected": st.column_config.NumberColumn("Encaissé", format="%.2f €"),
            "payment_date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
        }
    else:
        donnees = commandes_f[commandes_f["cart_id"].isin(paiements_statut["cart_id"])]
        colonnes = {
            "order_id": "Commande", "cart_id": "Panier", "user_id_pseudo": "Client (pseudonyme)",
            "product_id": "Produit", "product_title": "Libellé", "category": "Catégorie", "brand": "Marque",
            "quantity": "Quantité",
            "unit_price": st.column_config.NumberColumn("Prix unitaire", format="%.2f €"),
            "line_total": st.column_config.NumberColumn("Total ligne", format="%.2f €"),
            "discounted_line_total": st.column_config.NumberColumn("Total après remise", format="%.2f €"),
            "discount_percentage": st.column_config.NumberColumn("Remise (%)", format="%.2f"),
            "order_date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
        }

    st.caption(f"{len(donnees)} lignes")
    st.dataframe(donnees, width="stretch", hide_index=True, column_config=colonnes, height=480)
