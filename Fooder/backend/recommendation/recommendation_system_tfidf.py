# ============================================================
# CELL 1 — IMPORT LIBRARIES
# ============================================================

import re
import ast
import json
import warnings

import numpy as np
import pandas as pd

from pathlib import Path
from collections import defaultdict

# ------------------------------------------------------------
# MACHINE LEARNING
# ------------------------------------------------------------

from sklearn.feature_extraction.text import (
    TfidfVectorizer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)

# ------------------------------------------------------------
# EVALUATION
# ------------------------------------------------------------

from sklearn.model_selection import (
    train_test_split
)

# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

warnings.filterwarnings(
    "ignore"
)

RANDOM_STATE = 42

print(
    "Libraries imported successfully."
)
# ============================================================
# CELL 2 — CONFIGURATION
# ============================================================
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))
# ============================================================
# DATABASE IMPORT
# ============================================================

from Fooder.backend.database.db import (
    SessionLocal
)

from Fooder.backend.database.models import (
    Food
)
# ============================================================
# CELL 3 — LOAD DATABASE & AUDIT
# ============================================================

print(
    "Loading foods from database...\n"
)

# ------------------------------------------------------------
# LOAD FROM DATABASE
# ------------------------------------------------------------

session = SessionLocal()

foods = session.query(Food).all()

food_records = []

for food in foods:

    food_records.append(

        {

            "food_id":
                food.id,

            "food_name":
                str(
                    food.title_cleaned
                    or ""
                ),

            "ingredients":
                str(
                    food.ingredients_cleaned
                    or ""
                ),

            "category":
                str(
                    food.category
                    or ""
                ),

            "description":
                str(
                    food.description
                    or ""
                ),

            "origin_country":
                str(
                    food.origin_country
                    or ""
                ),

            "img_url":
                str(
                    food.img_url
                    or ""
                )

        }

    )

df_foods = pd.DataFrame(
    food_records
)

session.close()

# ------------------------------------------------------------
# DATASET SHAPE
# ------------------------------------------------------------

print(
    "Database Shape"
)

print(
    "-" * 50
)

print(
    f"Foods : {df_foods.shape}"
)

# ------------------------------------------------------------
# MISSING VALUES
# ------------------------------------------------------------

print(
    "\nMissing Values"
)

print(
    "-" * 50
)

print(
    df_foods.isnull().sum()
)

# ------------------------------------------------------------
# COLUMN INSPECTION
# ------------------------------------------------------------

print(
    "\nFood Columns"
)

print(
    "-" * 50
)

print(
    df_foods.columns.tolist()
)

# ------------------------------------------------------------
# DUPLICATE CHECK
# ------------------------------------------------------------

print(
    "\nDuplicate Check"
)

print(
    "-" * 50
)

print(
    f"Food Duplicates : "
    f"{df_foods.duplicated().sum():,}"
)
# ============================================================
# CELL 4 — TEXT CLEANING ENGINE
# ============================================================

def clean_text(text):

    """
    Universal text cleaning function
    untuk seluruh metadata makanan.
    """

    # --------------------------------------------------------
    # HANDLE NULL
    # --------------------------------------------------------

    if pd.isna(text):

        return ""

    # --------------------------------------------------------
    # TO STRING
    # --------------------------------------------------------

    text = str(text)

    # --------------------------------------------------------
    # LOWERCASE
    # --------------------------------------------------------

    text = text.lower()

    # --------------------------------------------------------
    # REMOVE NUMBERS
    # --------------------------------------------------------

    text = re.sub(

        r"\d+",

        " ",

        text

    )

    # --------------------------------------------------------
    # REMOVE SPECIAL CHARACTERS
    # --------------------------------------------------------

    text = re.sub(

        r"[^a-zA-Z\s]",

        " ",

        text

    )

    # --------------------------------------------------------
    # REMOVE EXTRA SPACES
    # --------------------------------------------------------

    text = re.sub(

        r"\s+",

        " ",

        text

    )

    return text.strip()
# ============================================================
# CELL 5 & 6 — FOOD MASTER FROM DATABASE
# ============================================================

print(
    "Building food master from database...\n"
)

# ------------------------------------------------------------
# CLEAN TEXT
# ------------------------------------------------------------

df_foods["food_name"] = (

    df_foods["food_name"]

    .fillna("")

    .apply(
        clean_text
    )

)

df_foods["ingredients_clean"] = (

    df_foods["ingredients"]

    .fillna("")

    .apply(
        clean_text
    )

)

df_foods["category_clean"] = (

    df_foods["category"]

    .fillna("")

    .apply(
        clean_text
    )

)

df_foods["description_clean"] = (

    df_foods["description"]

    .fillna("")

    .apply(
        clean_text
    )

)

df_foods["origin_country_clean"] = (

    df_foods["origin_country"]

    .fillna("")

    .apply(
        clean_text
    )

)

# ------------------------------------------------------------
# FOOD TEXT
# ------------------------------------------------------------

df_foods["food_text"] = (

    df_foods["food_name"] + " " +

    df_foods["food_name"] + " " +

    df_foods["food_name"] + " " +

    df_foods["ingredients_clean"] + " " +

    df_foods["category_clean"] + " " +

    df_foods["description_clean"] + " " +

    df_foods["origin_country_clean"]

)

# ------------------------------------------------------------
# FOOD MASTER
# ------------------------------------------------------------

food_master = (

    df_foods[

        [

            "food_id",

            "food_name",

            "food_text",

            "origin_country",

            "img_url"

        ]

    ]

    .copy()

)

# ------------------------------------------------------------
# REMOVE DUPLICATES
# ------------------------------------------------------------

food_master = (

    food_master

    .drop_duplicates(
        subset=["food_name"]
    )

    .reset_index(
        drop=True
    )

)

food_master = food_master[

    food_master["food_name"]
    != ""

]

food_master = food_master.reset_index(
    drop=True
)
# ============================================================
# FOOD TYPE DETECTION
# ============================================================

def detect_food_type(food_text):

    food_text = str(food_text).lower()

    if any(

        keyword in food_text

        for keyword in [

            "rice",
            "nasi"

        ]

    ):
        return "rice"

    if any(

        keyword in food_text

        for keyword in [

            "noodle",
            "ramen",
            "udon",
            "mie"

        ]

    ):
        return "noodles"

    if any(

        keyword in food_text

        for keyword in [

            "cake",
            "cookie",
            "dessert",
            "ice cream"

        ]

    ):
        return "dessert"

    if any(

        keyword in food_text

        for keyword in [

            "coffee",
            "tea",
            "juice",
            "drink"

        ]

    ):
        return "drink"

    if any(

        keyword in food_text

        for keyword in [

            "snack",
            "chips"

        ]

    ):
        return "snack"

    return "other"


# ============================================================
# CUISINE DETECTION
# ============================================================

def detect_cuisine_from_country(country):

    country = str(
        country
    ).lower()

    if "indonesia" in country:
        return "indonesian"

    if "korea" in country:
        return "korean"

    if "japan" in country:
        return "japanese"

    if "italy" in country:
        return "italian"

    if any(

        word in country

        for word in [

            "usa",
            "america",
            "united states"

        ]

    ):
        return "western"

    return "other"


# ============================================================
# EXTRA FEATURES
# ============================================================

food_master["food_type"] = (

    food_master["food_text"]

    .apply(
        detect_food_type
    )

)

food_master["cuisine"] = (

    food_master["origin_country"]

    .apply(
        detect_cuisine_from_country
    )

)
# ============================================================
# CELL 7 — TF-IDF ENGINE
# ============================================================

print(
    "Building TF-IDF matrix...\n"
)

# ------------------------------------------------------------
# TF-IDF CONFIGURATION
# ------------------------------------------------------------

tfidf = TfidfVectorizer(

    max_features=5000,

    stop_words="english",

    ngram_range=(1, 2),

    min_df=2,

    max_df=0.95

)

# ------------------------------------------------------------
# FIT TF-IDF
# ------------------------------------------------------------

tfidf_matrix = tfidf.fit_transform(

    food_master["food_text"]

)

# ------------------------------------------------------------
# VOCABULARY
# ------------------------------------------------------------

feature_names = (

    tfidf.get_feature_names_out()

)

# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

print(
    "TF-IDF Matrix Shape:"
)

print(
    tfidf_matrix.shape
)

print()

print(
    "Vocabulary Size:"
)

print(
    len(feature_names)
)

print()

print(
    "Sample Features:"
)

print(
    feature_names[:30]
)
# ============================================================
# CELL 8 — USER SESSION MODEL
# ============================================================

class UserSession:

    """
    Menyimpan seluruh preferensi user
    selama satu sesi penggunaan FooDer.
    """

    def __init__(self):

        # ----------------------------------------------------
        # SWIPE HISTORY
        # ----------------------------------------------------

        self.liked_foods = []

        self.disliked_foods = []

        # ----------------------------------------------------
        # FOOD REQUIREMENT
        # ----------------------------------------------------

        self.selected_requirements = []

        # Contoh:
        #
        # [
        #   "Halal",
        #   "Vegetarian",
        #   "No Seafood"
        # ]

        # ----------------------------------------------------
        # UI PREFERENCES
        # ----------------------------------------------------

        self.selected_moods = []

        # Contoh:
        #
        # [
        #   "Sweet",
        #   "Fresh"
        # ]

        self.selected_food_types = []

        # Contoh:
        #
        # [
        #   "Rice"
        # ]

        self.selected_cuisines = []

        # Contoh:
        #
        # [
        #   "Japanese"
        # ]

        # ----------------------------------------------------
        # SESSION PROFILE
        # ----------------------------------------------------

        self.today_taste_profile = {}

    # ========================================================
    # LIKE
    # ========================================================

    def add_like(

        self,
        food_id

    ):

        if food_id not in self.liked_foods:

            self.liked_foods.append(
                food_id
            )

    # ========================================================
    # DISLIKE
    # ========================================================

    def add_dislike(

        self,
        food_id

    ):

        if food_id not in self.disliked_foods:

            self.disliked_foods.append(
                food_id
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    def summary(self):

        return {

            "liked_foods":

                len(
                    self.liked_foods
                ),

            "disliked_foods":

                len(
                    self.disliked_foods
                ),

            "moods":

                self.selected_moods,

            "food_types":

                self.selected_food_types,

            "cuisines":

                self.selected_cuisines,

            "requirements":

                self.selected_requirements

        }

# ============================================================
# CREATE SESSION
# ============================================================

user_session = UserSession()

print(
    "User session initialized."
)
# ============================================================
# CELL 9 — SESSION QUERY BUILDER
# ============================================================

def build_session_query():

    """
    Menggabungkan seluruh makanan
    yang disukai user dalam sesi saat ini.
    """

    # --------------------------------------------------------
    # NO LIKES
    # --------------------------------------------------------

    if len(

        user_session.liked_foods

    ) == 0:

        return ""

    # --------------------------------------------------------
    # GET LIKED FOODS
    # --------------------------------------------------------

    liked_rows = food_master[

        food_master["food_id"]

        .isin(

            user_session.liked_foods

        )

    ]

    # --------------------------------------------------------
    # BUILD QUERY
    # --------------------------------------------------------

    session_query = " ".join(

        liked_rows["food_text"]

        .tolist()

    )

    return session_query
# ============================================================
# CELL 10 — USER PREFERENCE VECTOR
# ============================================================

def build_user_vector():

    """
    Mengubah seluruh preferensi user
    menjadi TF-IDF vector.
    """

    session_query = (
        build_session_query()
    )

    # ========================================================
    # FALLBACK TO UI PREFERENCES
    # ========================================================

    if len(session_query) == 0:

        query_parts = []

        for mood in user_session.selected_moods:

            mood = mood.lower()

            query_parts.append(mood)

            query_parts.extend(
                ATTRIBUTE_KEYWORDS.get(
                    mood,
                    []
                )
            )

        for food_type in user_session.selected_food_types:

            food_type = food_type.lower()

            query_parts.append(food_type)

            query_parts.extend(
                ATTRIBUTE_KEYWORDS.get(
                    food_type,
                    []
                )
            )

        for cuisine in user_session.selected_cuisines:

            cuisine = cuisine.lower()

            query_parts.append(cuisine)

            query_parts.extend(
                ATTRIBUTE_KEYWORDS.get(
                    cuisine,
                    []
                )
            )

        session_query = " ".join(
            query_parts
        )

    if len(session_query.strip()) == 0:
        return None

    user_vector = tfidf.transform(
        [session_query]
    )

    return user_vector
# ============================================================
# CELL 11 — CANDIDATE RETRIEVAL ENGINE
# ============================================================

def retrieve_candidates(
    top_k=300
):

    """
    Mengambil kandidat makanan
    berdasarkan preferensi sesi user.
    """

    user_vector = (
        build_user_vector()
    )

    if user_vector is None:

        return pd.DataFrame()

    # --------------------------------------------------------
    # SIMILARITY
    # --------------------------------------------------------

    similarity_scores = (

        cosine_similarity(

            user_vector,

            tfidf_matrix

        )

        .flatten()

    )

    # --------------------------------------------------------
    # CANDIDATES
    # --------------------------------------------------------

    candidates = (
        food_master.copy()
    )

    candidates[
        "similarity_score"
    ] = similarity_scores

    # --------------------------------------------------------
    # REMOVE LIKED FOODS
    # --------------------------------------------------------

    candidates = candidates[

        ~candidates["food_id"]

        .isin(

            user_session.liked_foods

        )

    ]

    # --------------------------------------------------------
    # REMOVE DISLIKED FOODS
    # --------------------------------------------------------

    candidates = candidates[

        ~candidates["food_id"]

        .isin(

            user_session.disliked_foods

        )

    ]

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    candidates = (

        candidates

        .sort_values(

            by="similarity_score",

            ascending=False

        )

    )

    return (

        candidates

        .head(top_k)

        .reset_index(
            drop=True
        )

    )
# ============================================================
# CELL 12 — FOOD ATTRIBUTE EXTRACTION
# ============================================================

ATTRIBUTE_KEYWORDS = {

    # --------------------------------------------------------
    # TASTE
    # --------------------------------------------------------

    "sweet": [

        "sweet",
        "honey",
        "sugar",
        "cake",
        "cookie",
        "dessert"

    ],

    "savory": [

        "savory",
        "beef",
        "chicken",
        "garlic",
        "onion"

    ],

    "spicy": [

        "spicy",
        "chili",
        "pepper",
        "sambal"

    ],

    "cheesy": [

        "cheese",
        "cream",
        "butter"

    ],

    "fresh": [

        "salad",
        "fruit",
        "vegetable",
        "fresh"

    ],

    # --------------------------------------------------------
    # PROTEIN
    # --------------------------------------------------------

    "beef": [

        "beef"

    ],

    "chicken": [

        "chicken"

    ],

    "seafood": [

        "fish",
        "shrimp",
        "crab",
        "lobster",
        "squid",
        "salmon",
        "tuna",
        "octopus",
        "anchovy",
        "eel"
    ],

    # --------------------------------------------------------
    # FOOD TYPE
    # --------------------------------------------------------

    "rice": [

        "rice",
        "nasi"

    ],

    "noodles": [

        "noodle",
        "ramen",
        "udon",
        "mie"

    ],

    "dessert": [

        "dessert",
        "cake",
        "cookie",
        "ice cream"

    ],

    "drink": [

        "coffee",
        "tea",
        "juice",
        "drink"

    ],

    "snack": [

        "snack",
        "chips"

    ],

    # --------------------------------------------------------
    # CUISINE
    # --------------------------------------------------------

    "indonesian": [

        "rendang",
        "sambal",
        "nasi",
        "bakso",
        "soto",
        "rawon",
        "gudeg",
        "pecel",
        "pempek",
        "sate",
        "ayam goreng",
        "ayam bakar",
        "nasi goreng"

    ],

    "korean": [

        "kimchi",
        "tteokbokki",
        "bibimbap",
        "bulgogi",
        "jajangmyeon",
        "japchae",
        "samgyeopsal",
        "dakgalbi"

    ],

    "japanese": [

        "sushi",
        "ramen",
        "udon",
        "sashimi",
        "tempura",
        "teriyaki",
        "yakitori"

    ],

    "western": [

        "burger",
        "steak",
        "western"

    ],

    "italian": [

        "pizza",
        "pasta",
        "italian"

    ]

}

# ============================================================
# ATTRIBUTE EXTRACTION
# ============================================================

def extract_food_attributes(
    food_text
):

    food_text = str(
        food_text
    ).lower()

    attributes = []

    for attribute, keywords in (

        ATTRIBUTE_KEYWORDS.items()

    ):

        for keyword in keywords:

            if keyword in food_text:

                attributes.append(
                    attribute
                )

                break

    return attributes
# ============================================================
# CELL 13 — TODAY'S TASTE PROFILE
# ============================================================

def build_today_taste_profile():

    """
    Membangun profil selera harian
    berdasarkan makanan yang di-like
    selama sesi berlangsung.
    """

    profile = defaultdict(float)

    # --------------------------------------------------------
    # NO LIKES
    # --------------------------------------------------------

    if len(

        user_session.liked_foods

    ) == 0:

        return {}

    # --------------------------------------------------------
    # GET LIKED FOODS
    # --------------------------------------------------------

    liked_rows = food_master[

        food_master["food_id"]

        .isin(

            user_session.liked_foods

        )

    ]

    # --------------------------------------------------------
    # EXTRACT ATTRIBUTES
    # --------------------------------------------------------

    for _, row in liked_rows.iterrows():

        attributes = (

            extract_food_attributes(

                row["food_text"]

            )

        )

        for attribute in attributes:

            profile[attribute] += 1

    # --------------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------------

    if len(profile) == 0:

        return {}

    max_score = max(

        profile.values()

    )

    for attribute in profile:

        profile[attribute] /= max_score

    return dict(profile)

# ============================================================
# BUILD PROFILE
# ============================================================

user_session.today_taste_profile = (

    build_today_taste_profile()

)

# ============================================================
# CELL 14 — UI PREFERENCE PROFILE
# ============================================================

MOOD_MAPPING = {

    "spicy": [
        "spicy"
    ],

    "sweet": [
        "sweet"
    ],

    "savory": [
        "savory"
    ],

    "cheesy": [
        "cheesy"
    ],

    "fresh": [
        "fresh"
    ]
}

FOOD_TYPE_MAPPING = {

    "rice": [
        "rice"
    ],

    "noodles": [
        "noodles"
    ],

    "snack": [
        "snack"
    ],

    "dessert": [
        "dessert"
    ],

    "drink": [
        "drink"
    ]
}

CUISINE_MAPPING = {

    "indonesian": [
        "indonesian"
    ],

    "korean": [
        "korean"
    ],

    "japanese": [
        "japanese"
    ],

    "western": [
        "western"
    ],

    "italian": [
        "italian"
    ]
}

# ============================================================
# CUISINE FILTER
# ============================================================

def apply_cuisine_filter(candidates):

    if candidates.empty:
        return candidates

    filtered = candidates.copy()

    if len(user_session.selected_cuisines) == 0:
        return filtered

    selected = [

        cuisine.lower()

        for cuisine in

        user_session.selected_cuisines

    ]

    filtered = filtered[

        filtered["cuisine"]

        .isin(selected)

    ]

    return filtered.reset_index(drop=True)

# ============================================================
# FOOD TYPE FILTER
# ============================================================

def apply_food_type_filter(candidates):

    if candidates.empty:
        return candidates

    filtered = candidates.copy()

    if len(user_session.selected_food_types) == 0:
        return filtered

    selected = [

        food_type.lower()

        for food_type in

        user_session.selected_food_types

    ]

    filtered = filtered[

        filtered["food_type"]

        .isin(selected)

    ]

    return filtered.reset_index(drop=True)
# ============================================================
# BUILD UI PROFILE
# ============================================================

def build_ui_preference_profile():

    profile = defaultdict(float)

    # --------------------------------------------------------
    # TASTE MOOD
    # --------------------------------------------------------

    for mood in user_session.selected_moods:

        mood = mood.lower()

        for attribute in (

            MOOD_MAPPING.get(
                mood,
                []
            )

        ):

            profile[
                attribute
            ] += 1

    # --------------------------------------------------------
    # FOOD TYPE
    # --------------------------------------------------------

    for food_type in (

        user_session
        .selected_food_types

    ):

        food_type = food_type.lower()

        for attribute in (

            FOOD_TYPE_MAPPING.get(
                food_type,
                []
            )

        ):

            profile[
                attribute
            ] += 1

    # --------------------------------------------------------
    # CUISINE
    # --------------------------------------------------------

    for cuisine in (

        user_session
        .selected_cuisines

    ):

        cuisine = cuisine.lower()

        for attribute in (

            CUISINE_MAPPING.get(
                cuisine,
                []
            )

        ):

            profile[
                attribute
            ] += 1

    return dict(profile)
# ============================================================
# CELL 15 — FOOD REQUIREMENT FILTER
# ============================================================

def apply_food_requirement_filter(
    candidates
):

    if candidates.empty:
        return candidates

    filtered = (
        candidates.copy()
    )

    requirements = [

        req.lower()

        for req in

        user_session
        .selected_requirements

    ]

    # --------------------------------------------------------
    # HALAL
    # --------------------------------------------------------

    if "halal" in requirements:

        haram_keywords = [

            "pork",
            "ham",
            "bacon",
            "wine",
            "beer"

        ]

        mask = ~filtered[
            "food_text"
        ].str.contains(

            "|".join(
                haram_keywords
            ),

            case=False,

            na=False

        )

        filtered = filtered[
            mask
        ]

    # --------------------------------------------------------
    # VEGETARIAN
    # --------------------------------------------------------

    if "vegetarian" in requirements:

        meat_keywords = [

            "beef",
            "chicken",
            "pork",
            "fish",
            "shrimp",
            "crab",
            "lobster",
            "squid"

        ]

        mask = ~filtered[
            "food_text"
        ].str.contains(

            "|".join(
                meat_keywords
            ),

            case=False,

            na=False

        )

        filtered = filtered[
            mask
        ]

    # --------------------------------------------------------
    # NO SEAFOOD
    # --------------------------------------------------------

    if "no seafood" in requirements:

        seafood_keywords = [

            "fish",
            "shrimp",
            "crab",
            "lobster",
            "squid",
            "salmon",
            "tuna",
            "cod",
            "octopus",
            "anchovy",
            "eel"
        ]

        mask = ~filtered[
            "food_text"
        ].str.contains(

            "|".join(
                seafood_keywords
            ),

            case=False,

            na=False

        )

        filtered = filtered[
            mask
        ]

    return (

        filtered

        .reset_index(
            drop=True
        )

    )

# ============================================================
# FILTER PIPELINE
# ============================================================

def apply_all_filters(candidates):

    candidates = apply_cuisine_filter(
        candidates
    )

    candidates = apply_food_type_filter(
        candidates
    )

    candidates = apply_food_requirement_filter(
        candidates
    )

    return candidates



# ============================================================
# CELL 16 — SHOW MY RECOMMENDATIONS
# ============================================================

def show_my_recommendations(
    candidates,
    top_n=10
):

    recommendations = (
        candidates.copy()
    )

    ui_profile = (
        build_ui_preference_profile()
    )

    taste_scores = []

    # --------------------------------------------------------
    # SCORING
    # --------------------------------------------------------

    for _, row in recommendations.iterrows():

        attributes = (

            extract_food_attributes(

                row["food_text"]

            )

        )

        score = 0

        # ----------------------------------------------------
        # TODAY'S TASTE PROFILE
        # ----------------------------------------------------

        for attribute in attributes:

            score += (

                user_session
                .today_taste_profile
                .get(
                    attribute,
                    0
                )

            )

        # ----------------------------------------------------
        # UI PROFILE
        # ----------------------------------------------------

        for attribute in attributes:

            score += (

                ui_profile
                .get(
                    attribute,
                    0
                )

            )

        taste_scores.append(
            score
        )

    recommendations[
        "taste_score"
    ] = taste_scores

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    recommendations[
        "final_score"
    ] = (

        recommendations[
            "similarity_score"
        ] * 0.4

        +

        recommendations[
            "taste_score"
        ] * 0.6

    )

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    recommendations = (

        recommendations

        .sort_values(

            by="final_score",

            ascending=False

        )

        .head(top_n)

        .reset_index(
            drop=True
        )

    )

    return recommendations

"""
# ============================================================
# CELL 17 — EVALUATION DATASET BUILDER
# ============================================================

print(
    "Building evaluation dataset..."
)

# ------------------------------------------------------------
# FILTER VALID RATINGS
# ------------------------------------------------------------

evaluation_df = (

    df_interactions

    .copy()

)

# ------------------------------------------------------------
# POSITIVE INTERACTIONS ONLY
# ------------------------------------------------------------

evaluation_df = evaluation_df[

    evaluation_df["rating"] >= 4

]

# ------------------------------------------------------------
# MINIMUM INTERACTIONS
# ------------------------------------------------------------

user_counts = (

    evaluation_df

    .groupby("user_id")

    .size()

)

valid_users = (

    user_counts[
        user_counts >= 5
    ]

    .index

)

evaluation_df = (

    evaluation_df[

        evaluation_df["user_id"]

        .isin(valid_users)

    ]

)

# ------------------------------------------------------------
# BUILD EVALUATION USERS
# ------------------------------------------------------------

evaluation_users = []

for user_id, group in (

    evaluation_df.groupby(
        "user_id"
    )

):

    foods = (

        group["recipe_id"]

        .tolist()

    )

    foods = list(

        dict.fromkeys(
            foods
        )

    )

    if len(foods) < 5:

        continue

    train_foods = foods[:-1]

    test_food = foods[-1]

    evaluation_users.append({

        "user_id":
            user_id,

        "train_foods":
            train_foods,

        "test_food":
            test_food

    })

# ------------------------------------------------------------
# TO DATAFRAME
# ------------------------------------------------------------

evaluation_users = pd.DataFrame(
    evaluation_users
)

print()

print(
    f"Evaluation Users : {len(evaluation_users):,}"
)

print()

print(
    evaluation_users.head()
)
"""
# ============================================================
# CELL 18 — EVALUATION VECTOR BUILDER
# ============================================================

def build_evaluation_query(
    train_foods
):

    """
    Membangun session query
    untuk user evaluasi.
    """

    liked_rows = food_master[

        food_master["food_id"]

        .isin(
            train_foods
        )

    ]

    if len(liked_rows) == 0:

        return ""

    query = " ".join(

        liked_rows["food_text"]

        .tolist()

    )

    return query


def build_evaluation_vector(
    train_foods
):

    """
    Mengubah train foods
    menjadi TF-IDF vector.
    """

    query = (

        build_evaluation_query(
            train_foods
        )

    )

    if len(query) == 0:

        return None

    vector = tfidf.transform(

        [query]

    )

    return vector

# ============================================================
# CELL 19 — HITRATE@K
# ============================================================

def hit_rate_at_k(

    evaluation_users,

    k=10,

    sample_size=200

):

    """
    Menghitung HitRate@K.
    """

    hits = 0

    total_users = 0

    evaluation_sample = (

        evaluation_users

        .sample(

            min(
                sample_size,
                len(evaluation_users)
            ),

            random_state=RANDOM_STATE

        )

    )

    for _, row in (

        evaluation_sample.iterrows()

    ):

        train_foods = row["train_foods"]

        test_food = row["test_food"]

        # ----------------------------------------------------
        # BUILD VECTOR
        # ----------------------------------------------------

        user_vector = (

            build_evaluation_vector(

                train_foods

            )

        )

        if user_vector is None:

            continue

        # ----------------------------------------------------
        # RETRIEVE
        # ----------------------------------------------------

        similarity_scores = (

            cosine_similarity(

                user_vector,

                tfidf_matrix

            )

            .flatten()

        )

        recommendations = (

            food_master.copy()

        )

        recommendations[
            "similarity_score"
        ] = similarity_scores

        recommendations = recommendations[

            ~recommendations["food_id"]

            .isin(
                train_foods
            )

        ]

        recommendations = (

            recommendations

            .sort_values(

                by="similarity_score",

                ascending=False

            )

            .head(k)

        )

        recommended_ids = (

            recommendations[
                "food_id"
            ]

            .tolist()

        )

        # ----------------------------------------------------
        # HIT
        # ----------------------------------------------------

        if test_food in recommended_ids:

            hits += 1

        total_users += 1

    if total_users == 0:

        return 0

    return hits / total_users
# ============================================================
# CELL 20 — PRECISION@K
# ============================================================

def precision_at_k(

    evaluation_users,

    k=10,

    sample_size=200

):

    """
    Menghitung Precision@K.
    """

    precision_scores = []

    evaluation_sample = (

        evaluation_users

        .sample(

            min(
                sample_size,
                len(evaluation_users)
            ),

            random_state=RANDOM_STATE

        )

    )

    for _, row in (

        evaluation_sample.iterrows()

    ):

        train_foods = row["train_foods"]

        test_food = row["test_food"]

        # ----------------------------------------------------
        # BUILD VECTOR
        # ----------------------------------------------------

        user_vector = (

            build_evaluation_vector(

                train_foods

            )

        )

        if user_vector is None:

            continue

        # ----------------------------------------------------
        # RETRIEVE
        # ----------------------------------------------------

        similarity_scores = (

            cosine_similarity(

                user_vector,

                tfidf_matrix

            )

            .flatten()

        )

        recommendations = (

            food_master.copy()

        )

        recommendations[
            "similarity_score"
        ] = similarity_scores

        recommendations = recommendations[

            ~recommendations["food_id"]

            .isin(
                train_foods
            )

        ]

        recommendations = (

            recommendations

            .sort_values(

                by="similarity_score",

                ascending=False

            )

            .head(k)

        )

        recommended_ids = (

            recommendations[
                "food_id"
            ]

            .tolist()

        )

        # ----------------------------------------------------
        # PRECISION
        # ----------------------------------------------------

        relevant_items = 0

        if test_food in recommended_ids:

            relevant_items = 1

        precision_scores.append(

            relevant_items / k

        )

    if len(precision_scores) == 0:

        return 0

    return np.mean(
        precision_scores
    )

# ============================================================
# CELL 21 — RECOMMENDATION QUALITY ANALYSIS
# ============================================================

def analyze_recommendation_quality(

    top_n=10

):

    recommendations = (

        show_my_recommendations(

            filtered_candidates,

            top_n=top_n

        )

    )

    print(
        "=" * 80
    )

    print(
        "USER SESSION SUMMARY"
    )

    print(
        "=" * 80
    )

    print()

    print(
        "Liked Foods:"
    )

    liked_rows = food_master[

        food_master["food_id"]

        .isin(

            user_session.liked_foods

        )

    ]

    print(

        liked_rows[
            "food_name"
        ]

        .tolist()

    )

    print()

    print(
        "Today's Taste Profile:"
    )

    print(
        user_session.today_taste_profile
    )

    print()

    print(
        "UI Preference Profile:"
    )

    print(
        build_ui_preference_profile()
    )

    print()

    print(
        "=" * 80
    )

    print(
        "TOP RECOMMENDATIONS"
    )

    print(
        "=" * 80
    )

    print()

    for rank, (_, row) in enumerate(

        recommendations.iterrows(),

        start=1

    ):

        attributes = (

            extract_food_attributes(

                row["food_text"]

            )

        )

        print(

            f"{rank}. {row['food_name']}"

        )

        print(

            f"   Similarity Score : "
            f"{row['similarity_score']:.4f}"

        )

        print(

            f"   Taste Score      : "
            f"{row['taste_score']:.4f}"

        )

        print(

            f"   Final Score      : "
            f"{row['final_score']:.4f}"

        )

        print(

            f"   Attributes       : "
            f"{attributes}"

        )
        print()
    return recommendations
