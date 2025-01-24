// Seleccionamos el cuadro de recomendaciones y la flecha
const recommendationsBox = document.getElementById('recommendations-box');
const toggleArrow = document.getElementById('toggle-arrow');
const arrow = toggleArrow.querySelector('.arrow');

// Agregamos el evento de clic a la flecha
toggleArrow.addEventListener('click', () => {
    // Alternar la clase 'expanded' en el cuadro
    recommendationsBox.classList.toggle('expanded');
    
    // Alternar la clase de la flecha entre 'down' y 'up'
    if (recommendationsBox.classList.contains('expanded')) {
        arrow.classList.remove('down');
        arrow.classList.add('up');
    } else {
        arrow.classList.remove('up');
        arrow.classList.add('down');
    }
});
