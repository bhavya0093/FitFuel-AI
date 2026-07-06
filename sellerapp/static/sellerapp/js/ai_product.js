document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("analyzeBtn");

    btn.addEventListener("click", function () {

        const formData = new FormData();

        formData.append(
            "product_name",
            document.getElementById("product_name").value
        );

        formData.append(
            "brand",
            document.getElementById("brand").value
        );

        formData.append(
            "description",
            document.getElementById("description").value
        );

        formData.append(
            "weight",
            document.getElementById("weight_unit").value
        );

        formData.append(
            "csrfmiddlewaretoken",
            document.querySelector("[name=csrfmiddlewaretoken]").value
        );

        btn.disabled = true;
        btn.innerHTML = "⏳ Analyzing...";

        fetch("/seller/analyze_product/", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(res => {

            btn.disabled = false;
            btn.innerHTML =
                '<i class="fa-solid fa-wand-magic-sparkles"></i> Analyze with AI';

            if (!res.success) {
                alert(res.message);
                return;
            }

            const d = res.data;

            document.getElementById("calories").value = d.calories;
            document.getElementById("protein").value = d.protein;
            document.getElementById("carbs").value = d.carbs;
            document.getElementById("fat").value = d.fat;
            document.getElementById("sugar").value = d.sugar;
            document.getElementById("fiber").value = d.fiber;
            document.getElementById("serving_size").value = d.serving_size;
            document.getElementById("diet_type").value = d.diet_type;
            document.getElementById("goal_type").value = d.goal_type;
            document.getElementById("flavour").value = d.flavour;
            document.getElementById("ingredients").value = d.ingredients;
            document.getElementById("benefits").value = d.benefits;
            document.getElementById("recommended_usage").value = d.recommended_usage;

        })
        .catch(err => {

            btn.disabled = false;
            btn.innerHTML =
                '<i class="fa-solid fa-wand-magic-sparkles"></i> Analyze with AI';

            console.log(err);
            alert("Something went wrong.");
        });

    });

});