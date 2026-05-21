const API_BASE_URL = "http://127.0.0.1:8000";

const pages = document.querySelectorAll(".page");
const navButtons = document.querySelectorAll(".nav");

const foodCard = document.querySelector(".food-card");
const rejectBtn = document.querySelector(".reject-btn");
const likeBtn = document.querySelector(".like-btn");
const starBtn = document.querySelector(".star-btn");

let foods = [];
let foodIndex = 0;
let startX = 0;
let currentX = 0;
let isDragging = false;

const fallbackFoods = [
  {
    id: 1,
    name: "Spicy Tteokbokki",
    restaurant: "Seoul Street Kitchen",
    img: "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=900&q=80",
    image: "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=900&q=80",
    rating: "4.8",
    reviews: "1284 reviews",
    distance: "0.6km",
    insight: "Most users love the bold spicy flavor and chewy texture for the price.",
    cuisine: "Korean · $$",
    tags: ["Spicy", "Savory", "Halal-friendly"]
  },
  {
    id: 2,
    name: "Double Smash Burger",
    restaurant: "Patty Garage",
    img: "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=900&q=80",
    image: "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=900&q=80",
    rating: "4.6",
    reviews: "942 reviews",
    distance: "1.2km",
    insight: "Reviewers rave about the crispy edges and juicy beef.",
    cuisine: "Western · $$",
    tags: ["Cheesy", "Beef", "Crispy"]
  },
  {
    id: 3,
    name: "Tonkotsu Ramen",
    restaurant: "Mengoku Ramen Bar",
    img: "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=900&q=80",
    image: "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=900&q=80",
    rating: "4.7",
    reviews: "2103 reviews",
    distance: "2.1km",
    insight: "Praised for rich creamy broth, tender toppings, and warm comfort taste.",
    cuisine: "Japanese · $$",
    tags: ["Savory", "Ramen", "Comfort"]
  }
];

async function fetchFoods() {
  try {
    const response = await fetch(`${API_BASE_URL}/restaurants`);
    const data = await response.json();

    foods = data.map((food) => ({
      ...food,
      img: food.img || food.image || "https://picsum.photos/300/200",
      image: food.image || food.img || "https://picsum.photos/300/200",
      reviews: food.count_rating || "0 reviews",
      cuisine: food.origin_country || "Food · $$",
      tags: food.tags || ["Recommended"],
      insight: food.insight || "This food is recommended based on rating and user preference.",
      distance: typeof food.distance === "number" ? `${food.distance}km` : food.distance
    }));

    if (foods.length === 0) {
      foods = fallbackFoods;
    }

    updateFoodCard();
  } catch (error) {
    console.error("Backend not connected, using fallback data:", error);
    foods = fallbackFoods;
    updateFoodCard();
  }
}

function showPage(pageId) {
  pages.forEach((page) => page.classList.remove("active"));
  document.getElementById(pageId).classList.add("active");

  navButtons.forEach((button) => button.classList.remove("active"));

  const pageNavMap = {
    homePage: 0,
    searchPage: 1,
    favoritePage: 2,
    nearbyPage: 3,
    profilePage: 4
  };

  if (pageNavMap[pageId] !== undefined) {
    navButtons[pageNavMap[pageId]].classList.add("active");
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
}

window.showPage = showPage;

function updateFoodCard() {
  if (!foodCard || foods.length === 0) return;

  const food = foods[foodIndex];

  document.querySelector(".food-card img").src = food.img || food.image;
  document.querySelector(".food-card h2").textContent = food.food_name;
  document.querySelector(".restaurant").textContent = food.restaurant_name;
  document.querySelector(".price-tag").textContent = food.cuisine;

  const infoItems = document.querySelectorAll(".food-info span");
  infoItems[0].textContent = `⭐ ${food.rating} (${String(food.reviews).split(" ")[0]})`;
  infoItems[1].textContent = `📍 ${food.distance}`;

  document.querySelector(".review-box p:last-child").textContent = food.insight;

  const tagBox = document.querySelector(".food-tags");
  tagBox.innerHTML = "";

  food.tags.forEach((tag) => {
    const span = document.createElement("span");
    span.textContent = tag;
    tagBox.appendChild(span);
  });

  foodCard.style.transition = "none";
  foodCard.style.transform = "translateX(0) rotate(0deg) scale(0.95)";

  setTimeout(() => {
    foodCard.style.transition = "0.25s ease";
    foodCard.style.transform = "translateX(0) rotate(0deg) scale(1)";
  }, 50);
}

async function saveSwipe(action) {
  if (foods.length === 0) return;

  try {
    await fetch(`${API_BASE_URL}/swipe`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        user_id: 1,
        food_id: foods[foodIndex].id || foodIndex + 1,
        action: action
      })
    });

    console.log(`Swipe ${action} saved`);
  } catch (error) {
    console.error("Failed to save swipe:", error);
  }
}

function nextFood() {
  foodIndex++;

  if (foodIndex >= foods.length) {
    foodIndex = 0;
  }

  updateFoodCard();
}

function swipeRight() {
  saveSwipe("like");

  foodCard.style.transition = "0.35s ease";
  foodCard.style.transform = "translateX(520px) rotate(25deg)";

  setTimeout(() => {
    nextFood();
  }, 350);
}

function swipeLeft() {
  saveSwipe("dislike");

  foodCard.style.transition = "0.35s ease";
  foodCard.style.transform = "translateX(-520px) rotate(-25deg)";

  setTimeout(() => {
    nextFood();
  }, 350);
}

function resetCard() {
  foodCard.style.transition = "0.3s ease";
  foodCard.style.transform = "translateX(0) rotate(0deg)";
}

function getClientX(event) {
  if (event.type.includes("mouse")) {
    return event.clientX;
  }

  return event.touches[0].clientX;
}

function startDrag(event) {
  isDragging = true;
  startX = getClientX(event);
  foodCard.style.transition = "none";
}

function dragCard(event) {
  if (!isDragging) return;

  currentX = getClientX(event) - startX;
  const rotate = currentX / 18;

  foodCard.style.transform = `translateX(${currentX}px) rotate(${rotate}deg)`;
}

function endDrag() {
  if (!isDragging) return;

  isDragging = false;

  if (currentX > 120) {
    swipeRight();
  } else if (currentX < -120) {
    swipeLeft();
  } else {
    resetCard();
  }

  currentX = 0;
}

if (foodCard) {
  foodCard.addEventListener("mousedown", startDrag);
  foodCard.addEventListener("touchstart", startDrag);

  document.addEventListener("mousemove", dragCard);
  document.addEventListener("touchmove", dragCard);

  document.addEventListener("mouseup", endDrag);
  document.addEventListener("touchend", endDrag);
}

if (rejectBtn) {
  rejectBtn.addEventListener("click", swipeLeft);
}

if (likeBtn) {
  likeBtn.addEventListener("click", swipeRight);
}

if (starBtn) {
  starBtn.addEventListener("click", () => {
    starBtn.classList.toggle("saved");
  });
}

function openFoodDetail(name, restaurant, image, rating, distance, insight, cuisine) {
  showPage("detailPage");

  const hero = document.querySelector(".detail-hero");

  hero.style.background = `
    linear-gradient(
      to bottom,
      rgba(0,0,0,.05),
      rgba(0,0,0,.85)
    ),
    url("${image}")
  `;

  hero.style.backgroundSize = "cover";
  hero.style.backgroundPosition = "center";

  document.querySelector(".detail-info h2").textContent = name;
  document.querySelector(".detail-info p").textContent = restaurant;
  document.querySelector(".detail-price").textContent = cuisine;

  const stats = document.querySelectorAll(".detail-stats b");
  const smallStats = document.querySelectorAll(".detail-stats small");

  stats[0].textContent = `⭐ ${rating}`;
  stats[1].textContent = `📍 ${distance}`;

  smallStats[0].textContent = "1284 reviews";
  smallStats[1].textContent = "from you";

  document.querySelector(".ai-summary > p").textContent = insight;

  const title = name.toLowerCase();

  if (title.includes("burger")) {
    document.querySelector(".desc").textContent =
      "A juicy double smash burger with crispy edges, melted cheese, fresh vegetables, and a soft toasted bun.";
    updateDetailTags(["Cheesy", "Beef", "Crispy"]);
    updateKeywords(["juicy", "crispy", "cheesy", "beefy"]);
    updateScore("74");
  } else if (title.includes("ramen")) {
    document.querySelector(".desc").textContent =
      "Warm Japanese ramen served with rich broth, noodles, egg, and savory toppings.";
    updateDetailTags(["Savory", "Comfort", "Japanese"]);
    updateKeywords(["broth", "creamy", "warm", "egg"]);
    updateScore("81");
  } else if (title.includes("sushi")) {
    document.querySelector(".desc").textContent =
      "Fresh salmon sushi platter served with rice, seaweed, soy sauce, and wasabi.";
    updateDetailTags(["Fresh", "Sushi", "Salmon"]);
    updateKeywords(["fresh", "clean", "salmon", "pretty"]);
    updateScore("78");
  } else if (title.includes("nasi")) {
    document.querySelector(".desc").textContent =
      "Classic Indonesian fried rice with smoky aroma, savory seasoning, egg, and local spices.";
    updateDetailTags(["Local", "Savory", "Affordable"]);
    updateKeywords(["smoky", "local", "savory", "filling"]);
    updateScore("86");
  } else {
    document.querySelector(".desc").textContent =
      "Chewy rice cakes simmered in a sweet-and-spicy gochujang sauce with fish cake and scallions.";
    updateDetailTags(["Spicy", "Savory", "Halal-friendly"]);
    updateKeywords(["spicy", "chewy", "affordable", "saucy", "addictive"]);
    updateScore("67");
  }
}

window.openFoodDetail = openFoodDetail;

function updateDetailTags(tags) {
  const tagContainer = document.querySelector(".detail-tags");
  if (!tagContainer) return;

  tagContainer.innerHTML = "";

  tags.forEach((tag) => {
    const span = document.createElement("span");
    span.textContent = tag;
    tagContainer.appendChild(span);
  });
}

function updateKeywords(keywords) {
  const keywordContainer = document.querySelector(".keywords");
  if (!keywordContainer) return;

  keywordContainer.innerHTML = "";

  keywords.forEach((keyword) => {
    const span = document.createElement("span");
    span.textContent = keyword;
    keywordContainer.appendChild(span);
  });
}

function updateScore(score) {
  const scoreTitle = document.querySelector(".score-card h4");
  if (!scoreTitle) return;

  scoreTitle.innerHTML = `${score} <span>/ 100 match for you</span>`;
}

const categoryButtons = document.querySelectorAll(".category");

categoryButtons.forEach((button) => {
  button.addEventListener("click", () => {
    categoryButtons.forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");
  });
});

const chips = document.querySelectorAll(".chips span");

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    const parent = chip.parentElement;

    parent.querySelectorAll("span").forEach((item) => {
      item.classList.remove("active");
    });

    chip.classList.add("active");
  });
});

const searchInput = document.querySelector(".search-box input");
const listCards = document.querySelectorAll(".list-card");

if (searchInput) {
  searchInput.addEventListener("input", () => {
    const keyword = searchInput.value.toLowerCase();

    listCards.forEach((card) => {
      const text = card.textContent.toLowerCase();

      if (text.includes(keyword)) {
        card.style.display = "flex";
      } else {
        card.style.display = "none";
      }
    });
  });
}

const saveButtons = document.querySelectorAll(
  ".fav-card button, .heart-detail, .save-btn"
);

saveButtons.forEach((button) => {
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    button.classList.toggle("saved");
  });
});

fetchFoods();
