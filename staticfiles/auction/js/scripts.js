try {
let slideIndex = 1;
showSlides(slideIndex);

// Next/previous controls
function changeSlide(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("slideshow_image");
  let dots = document.getElementsByClassName("dot");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";
  dots[slideIndex-1].className += " active";
}

let bpi = document.getElementById('bidPriceInput');
bpi.addEventListener("click", () => {
    console.log(bpi.value);
    let num = new String(bpi.value);
    num.replace(/[.,]/, '');
    cents = num.slice(num.length - 2, num.length);
    num = num.slice(0, num.length - 2);
    switch (num.length) {
        case 6:
            num = num.split(3).join(',');
            break;
        case 5:
            num = num.substring(0,2) + ',' + num.substring(2);
            break;
        case 4:
            num = num.substring(0,1) + ',' + num.substring(1);
            break;
    }
    // console.log(num + '.' + cents);
    bpi.value=(num + '.' + cents);
});

addEventListener('change', (e) => {
    console.log(e.target)
})
} catch {}