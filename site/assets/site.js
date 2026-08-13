const input=document.querySelector('[data-search]');
if(input)input.addEventListener('input',()=>document.querySelectorAll('[data-study]').forEach(x=>x.hidden=!x.textContent.toLowerCase().includes(input.value.toLowerCase())));
