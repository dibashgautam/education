document.addEventListener('DOMContentLoaded', function () {
    const confirmBtn = document.getElementById('confirmDeleteBtn');

    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const url = btn.getAttribute('data-delete-url');
            confirmBtn.href = url;  
        });
    });
});
