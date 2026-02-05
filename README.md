## FOR UNIQLO SCRAPING:
```
        What is given during scraping:
            productInfo --> {
                                    productId, 
                                    colors -> {
                                                name,
                                                code,
                                                displayCode
                                            },
                                    sizes.name,
                                    genderName, 
                                    genderCategory,
                                    productId,
                                    priceGroup,
                                    images -> {
                                                {displayCode}.image
                                            }, 
                                    name, 
                                    prices.base.value (assume USD)
                                    rating -> {
                                                average, 
                                                count
                                            }
                                    }
    
        ----------------------------------------------------------------------
    
        WIP structure for what we need: Each item in a list represents a single product
            uniqlo_products.csv --> [
                                        {
                                            id: uniqlo_{productId},
                                            brand: {BRAND},
                                            name: {name},
                                            category: {category},
                                            gender: {genderCategory},
                                            price: {prices.base.value},
                                            product_url: https://www.uniqlo.com/us/en/products/{productId}/{priceGroup}
                                            rating_avg: {rating.average},
                                            rating_count: {rating.count},
                                            variants: [
                                                        {
                                                            variant_id: {colors.code},
                                                            color: {colors.name},
                                                            sizes: [ size.name for size in sizes ],
                                                            image: {images.main.{displayCode}.image}
                                                        },
                                                        ...
                                                      ],
                                            scraped_at: {date.now()}
                                        },

                                        {...},
                                    ]
```
    