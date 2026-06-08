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

# Machine Learning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Evaluation
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

# Reproducibility
RANDOM_STATE = 42

print("Libraries imported successfully.")

NOTEBOOK_DIR = Path().resolve()

DATASET_DIR = NOTEBOOK_DIR.parent.parent / "Dataset"

PATHS = {

    "raw_recipes":
        DATASET_DIR / "RAW_recipes.csv",

    "raw_interactions":
        DATASET_DIR / "RAW_interactions.csv",

    "train_json":
        DATASET_DIR / "train.json",

    "indo_recipes":
        DATASET_DIR / "Indonesian_Food_Recipes.csv"
}

print("Dataset Verification")

missing_files = []

for dataset_name, dataset_path in PATHS.items():

    if dataset_path.exists():

        print(f"FOUND      | {dataset_name}")

    else:

        print(f"NOT FOUND  | {dataset_name}")

        missing_files.append(dataset_name)


if len(missing_files) == 0:

    print("All datasets verified successfully.")

else:

    print(
        f"Missing datasets: {missing_files}"
    )

# ============================================================
# CELL 3 — LOAD DATASET & AUDIT
# ============================================================

print("Loading datasets...\n")

# ============================================================
# LOAD DATASETS
# ============================================================

df_recipes = pd.read_csv(
    PATHS["raw_recipes"]
)

df_interactions = pd.read_csv(
    PATHS["raw_interactions"]
)

df_indo = pd.read_csv(
    PATHS["indo_recipes"]
)

# ============================================================
# DATASET SHAPE
# ============================================================

print("Dataset Shape")
print("-" * 50)

print(
    f"RAW Recipes         : {df_recipes.shape}"
)

print(
    f"Interactions        : {df_interactions.shape}"
)

print(
    f"Indonesian Recipes  : {df_indo.shape}"
)

# ============================================================
# MISSING VALUES
# ============================================================

print("\nMissing Values")
print("-" * 50)

print(
    df_recipes[
        ["name", "ingredients", "tags"]
    ]
    .isnull()
    .sum()
)

print()

print(
    df_indo[
        ["Title", "Ingredients"]
    ]
    .isnull()
    .sum()
)

# ============================================================
# COLUMN INSPECTION
# ============================================================

print("\nRAW Recipes Columns")
print("-" * 50)

print(
    df_recipes.columns.tolist()
)

print("\nIndonesian Recipes Columns")
print("-" * 50)

print(
    df_indo.columns.tolist()
)

def clean_text(text):
    """
    Universal text cleaning function
    untuk seluruh metadata makanan.
    """

    if pd.isna(text):
        return ""

    text = str(text).lower()

    # hapus angka
    text = re.sub(
        r"\d+",
        " ",
        text
    )

    # hapus simbol
    text = re.sub(
        r"[^a-zA-Z\s]",
        " ",
        text
    )

    # rapikan spasi
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()

# ============================================================
# CELL 5 — DATASET PREPARATION
# ============================================================

print("Preparing datasets...\n")

# ============================================================
# RAW RECIPES
# ============================================================

df_recipes = df_recipes.dropna(
    subset=["name"]
).copy()

df_recipes = df_recipes.sample(
    n=20000,
    random_state=RANDOM_STATE
).reset_index(drop=True)

df_recipes = df_recipes.rename(
    columns={
        "id": "food_id"
    }
)

# ============================================================
# INDONESIAN RECIPES
# ============================================================

df_indo = df_indo.copy()

# ============================================================
# SUMMARY
# ============================================================

print(
    f"Sampled Recipes      : {len(df_recipes):,}"
)

print(
    f"Indonesian Recipes   : {len(df_indo):,}"
)

# ============================================================
# CELL 6 — FOOD MASTER BUILDER
# ============================================================

print("Building food master...\n")

# ============================================================
# FOOD.COM DATASET
# ============================================================

df_recipes["food_name"] = (
    df_recipes["name"]
    .fillna("")
    .apply(clean_text)
)

df_recipes["ingredients_clean"] = (
    df_recipes["ingredients"]
    .fillna("")
    .apply(clean_text)
)

df_recipes["tags_clean"] = (
    df_recipes["tags"]
    .fillna("")
    .apply(clean_text)
)

df_recipes["food_text"] = (

    df_recipes["food_name"] + " " +
    df_recipes["food_name"] + " " +
    df_recipes["food_name"] + " " +

    df_recipes["ingredients_clean"] + " " +

    df_recipes["tags_clean"]

)

food_master_foodcom = df_recipes[
    [
        "food_id",
        "food_name",
        "food_text"
    ]
].copy()

food_master_foodcom["food_source"] = "foodcom"

# ============================================================
# INDONESIAN DATASET
# ============================================================

df_indo["food_name"] = (

    df_indo["Title"]
    .fillna("")
    .apply(clean_text)

)

df_indo["ingredients_clean"] = (

    df_indo["Ingredients"]
    .fillna("")
    .apply(clean_text)

)

df_indo["category_clean"] = (

    df_indo["Category"]
    .fillna("")
    .apply(clean_text)

)

df_indo["food_text"] = (

    df_indo["food_name"] + " " +
    df_indo["food_name"] + " " +
    df_indo["food_name"] + " " +

    df_indo["ingredients_clean"] + " " +

    df_indo["category_clean"]

)

food_master_indo = pd.DataFrame({

    "food_id":
        range(
            1000000,
            1000000 + len(df_indo)
        ),

    "food_name":
        df_indo["food_name"],

    "food_text":
        df_indo["food_text"],

    "food_source":
        "indonesia"
})

# ============================================================
# MERGE
# ============================================================

food_master = pd.concat(
    [
        food_master_foodcom,
        food_master_indo
    ],
    ignore_index=True
)

food_master = food_master.drop_duplicates(
    subset=["food_name"]
)

food_master = food_master.reset_index(
    drop=True
)

print(
    f"Total Foods : {len(food_master):,}"
)

print(
    f"food_master Shape: {food_master.shape}"
)
food_master.head()

# ============================================================
# CELL 7 — TF-IDF ENGINE
# ============================================================

print("Building TF-IDF matrix...\n")

tfidf = TfidfVectorizer(

    stop_words="english",

    max_features=5000,

    min_df=2

)

tfidf_matrix = tfidf.fit_transform(

    food_master["food_text"]

)

feature_names = tfidf.get_feature_names_out()

print("TF-IDF Matrix Shape:")
print(tfidf_matrix.shape)

print("\nVocabulary Size:")
print(len(feature_names))

print("\nSample Features:")
print(feature_names[:30])   

print("\n Shape TF-IDF Matrix:")
print(tfidf_matrix.shape)

# ============================================================
# CELL 8 — USER SESSION MODEL
# ============================================================

class UserSession:

    def __init__(self):

        # swipe hari ini
        self.liked_foods = []

        self.disliked_foods = []

        # hard constraints
        self.diet = None

        self.allergies = []

    def reset_session(self):

        self.liked_foods = []

        self.disliked_foods = []


user_session = UserSession()

print("User Session Initialized")

# ============================================================
# CELL 9 — SESSION QUERY BUILDER
# ============================================================

def build_session_query():

    """
    Menggabungkan seluruh makanan
    yang disukai user dalam sesi saat ini.
    """

    if len(user_session.liked_foods) == 0:

        return ""

    liked_rows = food_master[

        food_master["food_id"].isin(
            user_session.liked_foods
        )

    ]

    session_query = " ".join(

        liked_rows["food_text"]

    )

    return session_query

# ============================================================
# TEST
# ============================================================

sample_ids = (

    food_master
    .sample(
        3,
        random_state=RANDOM_STATE
    )["food_id"]
    .tolist()

)

user_session.liked_foods = sample_ids

session_query = build_session_query()

print("Liked Foods:")
print(sample_ids)

print("\nQuery Length:")
print(len(session_query))

print("\nQuery Preview:")
print(session_query[:300])

# ============================================================
# CELL 10 — USER PREFERENCE VECTOR
# ============================================================

def build_user_vector():

    """
    Mengubah session query
    menjadi TF-IDF vector user.
    """

    session_query = build_session_query()

    if len(session_query) == 0:

        return None

    user_vector = tfidf.transform(
        [session_query]
    )

    return user_vector

# ============================================================
# CELL 11 — CANDIDATE RETRIEVAL ENGINE
# ============================================================

def retrieve_candidates(
    top_k=50
):

    """
    Mengambil kandidat makanan
    berdasarkan preferensi sesi user.
    """

    user_vector = build_user_vector()

    if user_vector is None:

        return pd.DataFrame()

    similarity_scores = cosine_similarity(

        user_vector,
        tfidf_matrix

    ).flatten()

    candidates = food_master.copy()

    candidates["similarity_score"] = (
        similarity_scores
    )

    # --------------------------------------------------------
    # HAPUS MAKANAN YANG SUDAH DI-LIKE
    # --------------------------------------------------------

    candidates = candidates[

        ~candidates["food_id"].isin(
            user_session.liked_foods
        )

    ]

    # --------------------------------------------------------
    # HAPUS MAKANAN YANG DI-DISLIKE
    # --------------------------------------------------------

    candidates = candidates[

        ~candidates["food_id"].isin(
            user_session.disliked_foods
        )

    ]

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    candidates = candidates.sort_values(

        by="similarity_score",

        ascending=False

    )

    return candidates.head(top_k)

# ============================================================
# CELL 12 — FOOD ATTRIBUTE DICTIONARY
# ============================================================

FOOD_ATTRIBUTES = {

    "spicy": [
        "spicy",
        "chili",
        "sambal",
        "pepper",
        "hot"
    ],

    "sweet": [
        "sweet",
        "cake",
        "cookie",
        "dessert",
        "chocolate",
        "ice cream"
    ],

    "savory": [
        "savory",
        "fried",
        "garlic",
        "onion",
        "sauce"
    ],

    "beef": [
        "beef",
        "steak",
        "burger"
    ],

    "chicken": [
        "chicken",
        "ayam"
    ],

    "seafood": [
        "fish",
        "salmon",
        "shrimp",
        "crab",
        "tuna"
    ],

    "noodle": [
        "noodle",
        "ramen",
        "udon",
        "mie"
    ],

    "rice": [
        "rice",
        "nasi"
    ]
}


def extract_food_attributes(food_text):

    food_text = str(food_text).lower()

    attributes = []

    for attribute, keywords in FOOD_ATTRIBUTES.items():

        for keyword in keywords:

            if keyword in food_text:

                attributes.append(attribute)

                break

    return list(set(attributes))


print("Food Attribute Extractor Initialized")

sample_food = candidates.iloc[0]

print(
    sample_food["food_name"]
)

food_row = food_master[
    food_master["food_id"]
    ==
    sample_food["food_id"]
]

food_text = food_row.iloc[0]["food_text"]

print(
    extract_food_attributes(
        food_text
    )
)
print(
    extract_food_attributes(
        "beef burger with garlic sauce"
    )
)

class UserSession:

    def __init__(self):

        self.liked_foods = []

        self.disliked_foods = []

        self.diet = None

        self.allergies = []

        self.today_taste_profile = defaultdict(float)

    def reset_session(self):

        self.liked_foods = []

        self.disliked_foods = []

        self.today_taste_profile = defaultdict(float)

# ============================================================
# CELL 13 — TODAY'S TASTE PROFILE
# ============================================================

def build_today_taste_profile():

    """
    Membentuk profil selera hari ini
    berdasarkan swipe user.
    """

    taste_profile = defaultdict(float)

    # --------------------------------------------------------
    # LIKED FOODS
    # --------------------------------------------------------

    liked_rows = food_master[

        food_master["food_id"].isin(
            user_session.liked_foods
        )

    ]

    for _, row in liked_rows.iterrows():

        attributes = extract_food_attributes(
            row["food_text"]
        )

        for attribute in attributes:

            taste_profile[attribute] += 1

    # --------------------------------------------------------
    # DISLIKED FOODS
    # --------------------------------------------------------

    disliked_rows = food_master[

        food_master["food_id"].isin(
            user_session.disliked_foods
        )

    ]

    for _, row in disliked_rows.iterrows():

        attributes = extract_food_attributes(
            row["food_text"]
        )

        for attribute in attributes:

            taste_profile[attribute] -= 1

    user_session.today_taste_profile = (
        taste_profile
    )

    return dict(taste_profile)

# ============================================================
# CELL 14 — DIET & ALLERGY FILTER
# ============================================================

DIET_RULES = {

    "halal": [
        "pork",
        "bacon",
        "ham",
        "lard",
        "wine",
        "beer",
        "alcohol"
    ],

    "vegetarian": [
        "beef",
        "chicken",
        "fish",
        "shrimp",
        "crab",
        "tuna",
        "salmon",
        "pork"
    ],

    "vegan": [
        "beef",
        "chicken",
        "fish",
        "shrimp",
        "crab",
        "tuna",
        "salmon",
        "pork",
        "egg",
        "milk",
        "cheese",
        "butter",
        "yogurt"
    ]
}


ALLERGY_RULES = {

    "seafood": [
        "fish",
        "shrimp",
        "crab",
        "salmon",
        "tuna",
        "anchovy",
        "lobster",
        "clam",
        "oyster",
        "mussel"
    ],

    "egg": [
        "egg"
    ],

    "milk": [
        "milk",
        "cheese",
        "butter",
        "yogurt",
        "cream"
    ],

    "peanut": [
        "peanut",
        "groundnut"
    ],

    "gluten": [
        "wheat",
        "flour",
        "bread",
        "pasta",
        "noodle"
    ]
}

# ============================================================
# FOOD VALIDATION
# ============================================================

def is_food_allowed(food_text):

    food_text = str(food_text).lower()

    # --------------------------------------------------------
    # DIET FILTER
    # --------------------------------------------------------

    if user_session.diet is not None:

        restricted = DIET_RULES.get(
            user_session.diet,
            []
        )

        for ingredient in restricted:

            if ingredient in food_text:

                return False

    # --------------------------------------------------------
    # ALLERGY FILTER
    # --------------------------------------------------------

    for allergy in user_session.allergies:

        restricted = ALLERGY_RULES.get(
            allergy,
            []
        )

        for ingredient in restricted:

            if ingredient in food_text:

                return False

    return True

# ============================================================
# APPLY FILTER
# ============================================================

def apply_diet_allergy_filter(
    candidates
):

    filtered = candidates.copy()

    filtered = filtered[

        filtered["food_text"].apply(
            is_food_allowed
        )

    ]

    filtered = filtered.reset_index(
        drop=True
    )

    return filtered


filtered_candidates = (
    apply_diet_allergy_filter(
        candidates
    )
)

print(
    f"Before Filter : {len(candidates)}"
)

print(
    f"After Filter  : {len(filtered_candidates)}"
)
# ============================================================
# CELL 15 — FINAL FOOD RECOMMENDATIONS
# ============================================================

def generate_final_recommendations(
    filtered_candidates,
    top_n=10
):
    """
    Menghasilkan rekomendasi akhir FooDer.

    Semua kandidat sudah:
    - lolos TF-IDF retrieval
    - lolos diet filter
    - lolos allergy filter
    """

    recommendations = (

        filtered_candidates

        .sort_values(
            by="similarity_score",
            ascending=False
        )

        .head(top_n)

        .reset_index(drop=True)

    )

    return recommendations

# ============================================================
# CELL 16 — EVALUATION DATASET BUILDER
# ============================================================

print("Building evaluation dataset...")

# ------------------------------------------------------------
# POSITIVE INTERACTIONS ONLY
# ------------------------------------------------------------

positive_interactions = df_interactions[
    df_interactions["rating"] >= 4
].copy()

# ------------------------------------------------------------
# USER HISTORY
# ------------------------------------------------------------

user_histories = (

    positive_interactions

    .groupby("user_id")["recipe_id"]

    .apply(list)

)

# ------------------------------------------------------------
# MINIMUM INTERACTION FILTER
# ------------------------------------------------------------

user_histories = user_histories[
    user_histories.apply(len) >= 5
]

# ------------------------------------------------------------
# TRAIN / TEST SPLIT
# ------------------------------------------------------------

evaluation_users = []

for user_id, foods in user_histories.items():

    train_foods = foods[:-1]

    test_food = foods[-1]

    evaluation_users.append({

        "user_id": user_id,

        "train_foods": train_foods,

        "test_food": test_food

    })

evaluation_users = pd.DataFrame(
    evaluation_users
)

print(
    f"Evaluation Users: {len(evaluation_users):,}"
)

evaluation_users.head()

# ============================================================
# CELL 17A — EVALUATION RETRIEVAL
# ============================================================

def retrieve_candidates_for_evaluation(
    user_vector,
    train_foods,
    top_k=10
):
    """
    Candidate retrieval khusus evaluasi.
    Tidak menggunakan user_session.
    """

    similarity_scores = cosine_similarity(
        user_vector,
        tfidf_matrix
    ).flatten()

    candidates = food_master.copy()

    candidates["similarity_score"] = (
        similarity_scores
    )

    # ----------------------------------------
    # Hapus makanan train
    # ----------------------------------------

    candidates = candidates[

        ~candidates["food_id"].isin(
            train_foods
        )

    ]

    candidates = candidates.sort_values(
        by="similarity_score",
        ascending=False
    )

    return candidates.head(top_k)

# ============================================================
# CELL 17B — HIT RATE @ K
# ============================================================

def hit_rate_at_k(
    evaluation_users,
    k=10,
    sample_size=200
):

    hits = 0

    evaluation_subset = (

        evaluation_users

        .sample(

            min(
                sample_size,
                len(evaluation_users)
            ),

            random_state=42

        )

    )

    for _, row in evaluation_subset.iterrows():

        train_foods = row["train_foods"]

        test_food = row["test_food"]

        user_vector = build_evaluation_vector(
            train_foods
        )

        if user_vector is None:

            continue

        recommendations = (

            retrieve_candidates_for_evaluation(

                user_vector,

                train_foods,

                top_k=k

            )

        )

        recommended_ids = (
            recommendations["food_id"]
            .tolist()
        )

        if test_food in recommended_ids:

            hits += 1

    return hits / len(evaluation_subset)

# ============================================================
# CELL 18 — PRECISION @ K
# ============================================================

def precision_at_k(
    evaluation_users,
    k=10,
    sample_size=200
):

    precision_scores = []

    evaluation_subset = (

        evaluation_users

        .sample(

            min(
                sample_size,
                len(evaluation_users)
            ),

            random_state=42

        )

    )

    for _, row in evaluation_subset.iterrows():

        train_foods = row["train_foods"]

        test_food = row["test_food"]

        user_vector = build_evaluation_vector(
            train_foods
        )

        if user_vector is None:

            continue

        recommendations = (

            retrieve_candidates_for_evaluation(

                user_vector,

                train_foods,

                top_k=k

            )

        )

        recommended_ids = (
            recommendations["food_id"]
            .tolist()
        )

        relevant_count = 0

        if test_food in recommended_ids:

            relevant_count = 1

        precision_scores.append(
            relevant_count / k
        )

    return np.mean(
        precision_scores
    )

# ============================================================
# CELL 19 — RECOMMENDATION SIMILARITY ANALYSIS
# ============================================================

def analyze_food_similarity(
    food_name,
    top_k=10
):

    food_name = clean_text(
        food_name
    )

    matched = food_master[

        food_master["food_name"]
        ==
        food_name

    ]

    if len(matched) == 0:

        print(
            "Food not found."
        )

        return

    idx = matched.index[0]

    similarity_scores = cosine_similarity(

        tfidf_matrix[idx],

        tfidf_matrix

    ).flatten()

    similar_indices = (

        similarity_scores

        .argsort()

        [::-1]

    )

    similar_indices = [

        i

        for i in similar_indices

        if i != idx

    ]

    results = food_master.iloc[
        similar_indices[:top_k]
    ].copy()

    results["similarity_score"] = (

        similarity_scores[
            similar_indices[:top_k]
        ]

    )

    print(
        f"Query Food: {food_name}"
    )

    return results[
        [
            "food_name",
            "similarity_score"
        ]
    ]
