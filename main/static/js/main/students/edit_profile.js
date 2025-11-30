   

    // ----------------- Live Avatar Preview -----------------
const avatarInput = document.querySelector('input[name="avatar"]');
const avatarImg = document.getElementById('avatarImg');

avatarInput.addEventListener('change', function(){
    const file = this.files[0];
    if (file){
        const reader = new FileReader();
        reader.onload = function(e){
            avatarImg.setAttribute('src', e.target.result);
        }
        reader.readAsDataURL(file);
    }
});
