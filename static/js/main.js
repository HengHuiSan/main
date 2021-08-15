/*==================== CHANGE BACKGROUND HEADER ====================*/
function scrollHeader(){
    const header = document.getElementById('header')
    // When the scroll is greater than 100 viewport height, add the scroll-header class to the header tag
    if(this.scrollY >= 100) header.classList.add('scroll-header'); else header.classList.remove('scroll-header')
}
window.addEventListener('scroll', scrollHeader)


/*===== ACTIVE AND REMOVE MENU =====*/
// const navLink = document.querySelectorAll('.nav__link');   

// function linkAction(){
//   /*Active link*/
//   navLink.forEach(n => n.classList.remove('active'));
//   this.classList.add('active');
  
//   /*Remove menu mobile*/
//   const navMenu = document.getElementById('nav__menu')
//   navMenu.classList.remove('show')
// }
// navLink.forEach(n => n.addEventListener('click', linkAction));

