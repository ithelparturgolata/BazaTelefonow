let selection = document.querySelector('select');
let result = document.querySelector('textarea');
selection.addEventListener('change', () => {
    result.innerText = selection.options[selection.selectedIndex].value;
    console.log(selection.selectedIndex);
});