console.log("Base JS Loaded");
console.log("Home JS loaded");
// Search
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    searchInput.addEventListener('keyup', function() {
        const query = this.value.trim();
        console.log('Searching for:', query); // Debug
        
        if(query.length === 0) {
            searchResults.style.display = 'none';
            searchResults.innerHTML = '';
            return;
        }

        searchResults.innerHTML = '<div class="p-2 text-center">Searching...</div>';
        searchResults.style.display = 'block';

        fetch(`/ajax-search/?q=${encodeURIComponent(query)}`)
            .then(res => {
                console.log('Response status:', res.status); // Debug
                if (!res.ok) {
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                return res.json();
            })
            .then(data => {
                console.log('Data received:', data); // Debug
                searchResults.innerHTML = data.html;
                searchResults.style.display = 'block';
            })
            .catch(error => {
                console.error('Fetch error:', error);
                searchResults.innerHTML = '<div class="p-2 text-center text-danger">Error: ' + error.message + '</div>';
            });
    });

    // Click outside to close
    document.addEventListener('click', function(e) {
        if (!searchResults.contains(e.target) && e.target !== searchInput) {
            searchResults.style.display = 'none';
        }
    });

    // Handle item clicks
    searchResults.addEventListener('click', function(e) {
        let target = e.target;
        while (target && !target.classList.contains('search-item')) {
            target = target.parentElement;
        }
        if (target && target.getAttribute('data-url')) {
            window.location.href = target.getAttribute('data-url');
        }
    });
});
