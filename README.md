# Bharat Business

**Indian Small Business Operating Platform** built on [Frappe Framework](https://frappeframework.com/) and [ERPNext](https://erpnext.com/).

Bharat Business wraps ERPNext's proven business engine with a simplified, mobile-first experience designed for Indian small and medium businesses.

## Supported Business Types

- Retail shops
- Grocery and convenience stores
- Wholesale and distribution
- Restaurants and cafes
- Repair and service businesses
- Freelancers and agencies
- Small manufacturing

## Technology Stack

| Component | Version |
|-----------|---------|
| Frappe Framework | version-16 |
| ERPNext | v16.53.x |
| India Compliance | version-16 |
| MariaDB | 11.8 |
| Python | 3.10+ |

## Development Setup

Follow the [frappe_docker development guide](https://github.com/Mangalbaskey/frappe_docker) to set up the devcontainer environment.

```bash
# Inside the devcontainer
bench get-app https://github.com/resilient-tech/india-compliance --branch version-16
bench get-app https://github.com/<your-org>/bharat_business --branch main
bench --site <site-name> install-app india_compliance
bench --site <site-name> install-app bharat_business
```

## License

MIT
