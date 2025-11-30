(function(){
  const bgInput = document.getElementById('id_background_image');
  const bgImg = document.getElementById('bgImg');
  const logoInput = document.getElementById('id_logo_image');
  const logoInner = document.getElementById('logoInner');
  const regInput = document.getElementById('id_registration_image');
  const regPreviewImg = document.getElementById('regPreviewImg');

  bgInput.addEventListener('change', e=>{
    const file = e.target.files[0];
    if(!file) return;
    const reader = new FileReader();
    reader.onload = ev => bgImg.src = ev.target.result;
    reader.readAsDataURL(file);
  });

  logoInput.addEventListener('change', e=>{
    const file = e.target.files[0];
    if(!file) return;
    const reader = new FileReader();
    reader.onload = ev=>{
      logoInner.innerHTML = `<img src="${ev.target.result}" style="width:100px;height:100px;border-radius:50%;">`;
    };
    reader.readAsDataURL(file);
  });

})();
