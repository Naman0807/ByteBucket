const hamburger = document.getElementById("hamburger");
const mobileMenu = document.getElementById("mobile-menu");

hamburger.addEventListener("click", () => {
	if (mobileMenu.classList.contains("-translate-x-full")) {
		mobileMenu.classList.remove("-translate-x-full");
		mobileMenu.classList.add("translate-x-0");
	} else {
		mobileMenu.classList.remove("translate-x-0");
		mobileMenu.classList.add("-translate-x-full");
	}
});

// Optional: Close the menu if a link is clicked (for smoother user experience)
document.querySelectorAll("#mobile-menu a").forEach((link) => {
	link.addEventListener("click", () => {
		mobileMenu.classList.remove("translate-x-0");
		mobileMenu.classList.add("-translate-x-full");
	});
});

// Listen to the search button click
document.getElementById("search-button").addEventListener("click", function () {
	const query = document.getElementById("search-input").value.toLowerCase();

	// Get all file items and category containers
	const fileItems = document.querySelectorAll(".file-item");
	const categories = document.querySelectorAll(".category-container");

	// Track which categories contain matching files
	let categoriesWithMatches = new Set();

	// Filter the files based on the search query
	fileItems.forEach(function (item) {
		const fileName = item.getAttribute("data-file").toLowerCase();
		const categoryName = item.getAttribute("data-category");

		// Check if the file name includes the query
		if (fileName.includes(query)) {
			item.style.display = "flex"; // Show matching items
			categoriesWithMatches.add(categoryName); // Mark category as having a match
		} else {
			item.style.display = "none"; // Hide non-matching items
		}
	});

	// Show or hide categories based on whether they have matching files
	categories.forEach(function (category) {
		const categoryId = category.id.replace("category-", "");
		if (categoriesWithMatches.has(categoryId)) {
			category.style.display = "block"; // Show categories with matches
		} else {
			category.style.display = "none"; // Hide categories without matches
		}
	});
});

// Also listen for Enter keypress on the search input field
document
	.getElementById("search-input")
	.addEventListener("keypress", function (event) {
		if (event.key === "Enter") {
			event.preventDefault();
			document.getElementById("search-button").click();
		}
	});
