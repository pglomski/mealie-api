# Mealie API Wrapper

This is a lightweight Python wrapper around the [Mealie API](https://docs.mealie.io/api/), designed for simple, authenticated access to self-hosted Mealie servers. It enables programmatic interaction with recipes, categories, tags, and other Mealie objects in a clean, Pythonic interface.

---

## 🔧 Features

- ✅ Authentication with Mealie's API token system
- 📄 Retrieve and manipulate recipes
- 🏷️ Access and manage tags and categories
- 📂 Interact with collections and meal plans *(in progress)*
- 🧪 Simple, testable interface for integrating Mealie into other apps or automations

---

## 🚀 Quick Start

### 📦 Installation

```bash
pip install git+https://github.com/pglomski/mealie-api.git
```

Or clone locally:

```bash
git clone https://github.com/pglomski/mealie-api.git
cd mealie-api
pip install .
```

---

### 📝 Usage

```python
from mealie import MealieClient

client = MealieClient(
    url="https://your-mealie-url.com",
    token="your_api_token"
)

# Fetch a list of recipes
recipes = client.recipes.list()

# Get a single recipe by slug
recipe = client.recipes.get("my-best-pancakes")

# Create a new recipe (basic example)
new_recipe = client.recipes.create({
    "name": "Simple Stir Fry",
    "description": "Fast, easy, and healthy!"
})
```

See [examples](examples/) for more usage patterns.

---

## 🔐 Authentication

Authentication is handled via an API token, which can be generated from your Mealie user profile under **Settings → API Tokens**.

---

## 📚 Documentation

- Mealie API Reference: https://docs.mealie.io/api/
- This wrapper's API follows the structure and endpoints of the official Mealie API.
- See the `mealie/` directory for client implementations.

---

## 🧪 Testing

Basic test coverage is planned but not fully implemented. If you'd like to contribute tests, see [CONTRIBUTING.md](CONTRIBUTING.md) *(planned)*.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request if you find a bug or want to add features.

---

## 📄 License

This project is licensed under the GPL-3.0 License. See [`LICENSE`](LICENSE) for details.

---

## 🙋 FAQ

**Q: Does this work with Mealie v1 or v2?**  
A: This package targets Mealie v1.x APIs. Compatibility with v2+ may require updates.

**Q: Can I upload images or media with this wrapper?**  
A: Not yet. File upload support is on the roadmap.

---

## ✨ Acknowledgments

Built to work with [Mealie](https://github.com/hay-kot/mealie), a fantastic self-hosted recipe manager by [hay-kot](https://github.com/hay-kot).

