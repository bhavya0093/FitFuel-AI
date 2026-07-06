document.addEventListener("DOMContentLoaded", function () {

const steps = document.querySelectorAll(".step");

const nextBtn = document.getElementById("nextBtn");

const prevBtn = document.getElementById("prevBtn");

const submitBtn = document.getElementById("submitBtn");

const progressFill = document.querySelector(".progress-fill");

const progressText = document.querySelector(".progress-text");

let currentStep = 0;

showStep(currentStep);

function showStep(step){

    steps.forEach(s=>s.classList.remove("active-step"));

    steps[step].classList.add("active-step");

    progressFill.style.width=((step+1)/steps.length)*100+"%";

    progressText.innerHTML="Step "+(step+1)+" of "+steps.length;

    prevBtn.style.display=step===0?"none":"inline-block";

    nextBtn.style.display=step===steps.length-1?"none":"inline-block";

    submitBtn.style.display=step===steps.length-1?"inline-block":"none";

}

nextBtn.addEventListener("click",function(){

    if(currentStep<steps.length-1){

        currentStep++;

        showStep(currentStep);

    }

});

prevBtn.addEventListener("click",function(){

    if(currentStep>0){

        currentStep--;

        showStep(currentStep);

    }

});

});