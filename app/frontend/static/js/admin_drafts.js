const deleteButtons = document.querySelectorAll(
    ".delete-draft-button"
);


deleteButtons.forEach((button) => {

    button.addEventListener(
        "click",
        async () => {

            const draftId =
                button.dataset.draftId;

            const draftTitle =
                button.dataset.draftTitle;


            const confirmed = confirm(
                `Delete draft "${draftTitle}"?\n\n`
                + "This action cannot be undone."
            );


            if (!confirmed) {
                return;
            }


            button.disabled = true;
            button.textContent = "Deleting...";


            try {

                const response = await fetch(
                    `/admin/posts/drafts/${draftId}`,
                    {
                        method: "DELETE"
                    }
                );


                if (!response.ok) {

                    let message =
                        "Unable to delete draft.";

                    try {

                        const result =
                            await response.json();

                        if (result.detail) {
                            message =
                                result.detail;
                        }

                    } catch {
                    }


                    throw new Error(message);
                }


                window.location.reload();


            } catch (error) {

                alert(error.message);

                button.disabled = false;
                button.textContent = "Delete";
            }

        }
    );

});