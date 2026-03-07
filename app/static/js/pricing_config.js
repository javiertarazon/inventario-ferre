document.addEventListener('DOMContentLoaded', function () {
    const page = document.getElementById('pricingConfigPage');
    if (!page) {
        return;
    }

    const searchUrl = page.dataset.searchUrl || '/pricing/search-products';
    const applyTo = document.getElementById('apply_to');
    const categorySelect = document.getElementById('categorySelect');
    const productSearch = document.getElementById('productSearch');
    const productSearchInput = document.getElementById('product_search');
    const productResults = document.getElementById('productResults');
    const productIdInput = document.getElementById('product_id');
    const searchButton = document.getElementById('searchBtn');
    const searchQueryInput = document.getElementById('searchQuery');
    const searchCategoryInput = document.getElementById('searchCategory');
    const searchProveedorInput = document.getElementById('searchProveedor');
    const pricingResults = document.getElementById('pricingSearchResults');

    let productSearchTimeout;

    function renderSearchError(message) {
        pricingResults.innerHTML = '<div class="alert alert-danger"><i class="bi bi-exclamation-circle"></i> ' + message + '</div>';
    }

    function renderPricingResults(data) {
        if (!data.products || data.products.length === 0) {
            pricingResults.innerHTML = '<div class="alert alert-info">No se encontraron productos</div>';
            return;
        }

        let html = [
            '<div class="alert alert-success">',
            '<strong>Tasa actual: ' + data.rate.toFixed(2) + ' Bs/$</strong> | ',
            'Productos encontrados: ' + data.count,
            '</div>',
            '<div class="table-responsive">',
            '<table class="table table-hover">',
            '<thead>',
            '<tr>',
            '<th>Codigo</th>',
            '<th>Descripcion</th>',
            '<th>Categoria</th>',
            '<th>Proveedor</th>',
            '<th>Precio USD</th>',
            '<th>Precio Bs</th>',
            '<th>Factor</th>',
            '<th>Precio Final Bs</th>',
            '</tr>',
            '</thead>',
            '<tbody>'
        ].join('');

        data.products.forEach(function (product) {
            html += [
                '<tr>',
                '<td><strong>' + product.codigo + '</strong></td>',
                '<td>' + product.descripcion + '</td>',
                '<td><span class="badge bg-secondary">' + product.categoria + '</span></td>',
                '<td><span class="badge bg-dark">' + product.proveedor + '</span></td>',
                '<td>$' + product.precio_dolares.toFixed(2) + '</td>',
                '<td>' + product.precio_bs.toFixed(2) + ' Bs</td>',
                '<td>' + product.factor_ajuste.toFixed(2) + '</td>',
                '<td><strong>' + product.precio_final_bs.toFixed(2) + ' Bs</strong></td>',
                '</tr>'
            ].join('');
        });

        html += '</tbody></table></div>';
        pricingResults.innerHTML = html;
    }

    function searchProducts() {
        const params = new URLSearchParams();
        const query = searchQueryInput.value.trim();
        const category = searchCategoryInput.value;
        const proveedor = searchProveedorInput.value;

        if (query) {
            params.set('q', query);
        }
        if (category) {
            params.set('category_id', category);
        }
        if (proveedor) {
            params.set('proveedor_id', proveedor);
        }

        const requestUrl = params.toString() ? searchUrl + '?' + params.toString() : searchUrl;

        fetch(requestUrl, {
            credentials: 'same-origin'
        })
            .then(function (response) {
                if (!response.ok) {
                    if (response.status === 401) {
                        throw new Error('Sesion expirada. Inicie sesion nuevamente.');
                    }
                    throw new Error('Error ' + response.status + ': No se pudo recuperar los datos.');
                }
                return response.json();
            })
            .then(function (data) {
                if (!data.success) {
                    throw new Error(data.error || 'Error desconocido');
                }
                renderPricingResults(data);
            })
            .catch(function (error) {
                renderSearchError(error.message);
            });
    }

    function searchProductsForFactor(query) {
        fetch(searchUrl + '?q=' + encodeURIComponent(query), {
            credentials: 'same-origin'
        })
            .then(function (response) {
                if (!response.ok) {
                    throw new Error('No se pudo buscar productos');
                }
                return response.json();
            })
            .then(function (data) {
                if (!data.success || !data.products || data.products.length === 0) {
                    productResults.innerHTML = '<div class="alert alert-warning">No se encontraron productos</div>';
                    return;
                }

                let html = '';
                data.products.forEach(function (product) {
                    html += '<a href="#" class="list-group-item list-group-item-action" data-id="' + product.id + '" data-codigo="' + product.codigo + '">' +
                        '<strong>' + product.codigo + '</strong> - ' + product.descripcion +
                        '</a>';
                });

                productResults.innerHTML = html;
                productResults.querySelectorAll('a').forEach(function (item) {
                    item.addEventListener('click', function (event) {
                        event.preventDefault();
                        productIdInput.value = this.dataset.id;
                        productSearchInput.value = this.dataset.codigo;
                        productResults.innerHTML = '';
                    });
                });
            })
            .catch(function () {
                productResults.innerHTML = '<div class="alert alert-danger">Error al buscar productos</div>';
            });
    }

    applyTo.addEventListener('change', function () {
        categorySelect.style.display = 'none';
        productSearch.style.display = 'none';

        if (this.value === 'category') {
            categorySelect.style.display = 'block';
        } else if (this.value === 'product') {
            productSearch.style.display = 'block';
        }
    });

    productSearchInput.addEventListener('input', function () {
        clearTimeout(productSearchTimeout);
        const query = this.value.trim();

        if (query.length < 2) {
            productResults.innerHTML = '';
            return;
        }

        productSearchTimeout = setTimeout(function () {
            searchProductsForFactor(query);
        }, 300);
    });

    searchButton.addEventListener('click', searchProducts);
    searchQueryInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            searchProducts();
        }
    });
    searchCategoryInput.addEventListener('change', searchProducts);
    searchProveedorInput.addEventListener('change', searchProducts);
});
