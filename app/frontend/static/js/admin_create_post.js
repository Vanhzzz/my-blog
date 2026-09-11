const editor = document.getElementById("post-editor");

const titleInput = document.getElementById("post-title");
const slugInput = document.getElementById("post-slug");
const summaryInput = document.getElementById("post-summary");
const categoryInput = document.getElementById("post-category");
const contentInput = document.getElementById("post-content");
const coverImageUrlInput = document.getElementById(
    "cover-image-url"
);

const saveStatus = document.getElementById("save-status");
const saveStatusDot = document.getElementById(
    "save-status-dot"
);

const previewButton = document.getElementById(
    "preview-button"
);

const publishButton = document.getElementById(
    "publish-button"
);

const insertCodeButton = document.getElementById(
    "insert-code-button"
);


let draftId = editor.dataset.draftId
    ? Number(editor.dataset.draftId)
    : null;

let autosaveTimer = null;

let isSaving = false;

let pendingSave = false;

let slugWasEdited = Boolean(
    slugInput.value.trim()
);

let lastSavedData = null;


const AUTOSAVE_DELAY = 1200;


/* ==============================
   DATA
   ============================== */

function getPostData() {
    return {
        title: titleInput.value,
        slug: slugInput.value,
        summary: summaryInput.value,
        category: categoryInput.value,
        content: contentInput.value,
        cover_image_url: (
            coverImageUrlInput.value || null
        )
    };
}


function hasContent(data) {
    return Boolean(
        data.title.trim()
        || data.slug.trim()
        || data.summary.trim()
        || data.category.trim()
        || data.content.trim()
        || data.cover_image_url
    );
}


function dataChanged(data) {
    return (
        JSON.stringify(data)
        !== JSON.stringify(lastSavedData)
    );
}


/* ==============================
   SAVE STATUS
   ============================== */

function setSaveStatus(state, text) {
    saveStatus.textContent = text;

    saveStatusDot.classList.remove(
        "saving",
        "saved",
        "error"
    );

    if (state) {
        saveStatusDot.classList.add(state);
    }
}


/* ==============================
   SLUG
   ============================== */

function generateSlug(value) {
    return value
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/đ/g, "d")
        .replace(/Đ/g, "D")
        .toLowerCase()
        .trim()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");
}


titleInput.addEventListener("input", () => {
    if (!slugWasEdited) {
        slugInput.value = generateSlug(
            titleInput.value
        );
    }
});


slugInput.addEventListener("input", () => {
    slugWasEdited = true;
});


/* ==============================
   AUTOSAVE
   ============================== */

function scheduleAutosave() {
    clearTimeout(autosaveTimer);

    setSaveStatus(
        null,
        "Unsaved changes"
    );

    autosaveTimer = setTimeout(
        () => {
            saveDraft();
        },
        AUTOSAVE_DELAY
    );
}


async function saveDraft(force = false) {
    const data = getPostData();

    if (!force && !hasContent(data)) {
        return draftId;
    }

    if (
        !force
        && !dataChanged(data)
    ) {
        return draftId;
    }

    if (isSaving) {
        pendingSave = true;

        return draftId;
    }

    isSaving = true;
    pendingSave = false;

    setSaveStatus(
        "saving",
        "Saving..."
    );

    try {
        let url;
        let method;

        if (draftId) {
            url = (
                `/admin/posts/drafts/`
                + `${draftId}/autosave`
            );

            method = "PUT";
        } else {
            url = "/admin/posts/autosave";

            method = "POST";
        }


        const response = await fetch(
            url,
            {
                method: method,

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(data)
            }
        );


        if (!response.ok) {
            throw new Error(
                "Autosave failed."
            );
        }


        const result = await response.json();


        if (!draftId) {
            draftId = result.draft_id;

            editor.dataset.draftId = draftId;

            history.replaceState(
                {},
                "",
                `/admin/posts/drafts/`
                + `${draftId}/edit`
            );
        }


        lastSavedData = data;


        setSaveStatus(
            "saved",
            "Saved"
        );


        return draftId;

    } catch (error) {

        console.error(error);

        setSaveStatus(
            "error",
            "Save failed"
        );

        throw error;

    } finally {

        isSaving = false;


        if (pendingSave) {
            pendingSave = false;

            saveDraft();
        }
    }
}


/* ==============================
   INPUT EVENTS
   ============================== */

const autosaveInputs = [
    titleInput,
    slugInput,
    summaryInput,
    categoryInput,
    contentInput
];


autosaveInputs.forEach((input) => {
    input.addEventListener(
        "input",
        scheduleAutosave
    );
});


/* ==============================
   PREVIEW
   ============================== */

previewButton.addEventListener(
    "click",
    async () => {

        const previewWindow = window.open(
            "about:blank",
            "_blank"
        );


        try {

            clearTimeout(autosaveTimer);

            await saveDraft(true);


            if (!draftId) {
                throw new Error(
                    "Draft could not be created."
                );
            }


            previewWindow.location.href = (
                `/admin/posts/drafts/`
                + `${draftId}/preview`
            );

        } catch (error) {

            if (previewWindow) {
                previewWindow.close();
            }


            alert(
                "Unable to open preview."
            );
        }
    }
);


/* ==============================
   PUBLISH
   ============================== */

publishButton.addEventListener(
    "click",
    async () => {

        publishButton.disabled = true;

        publishButton.textContent =
            "Publishing...";


        try {

            clearTimeout(autosaveTimer);

            await saveDraft(true);


            if (!draftId) {
                throw new Error(
                    "Draft does not exist."
                );
            }


            const response = await fetch(
                `/admin/posts/drafts/`
                + `${draftId}/publish`,
                {
                    method: "POST"
                }
            );


            const result = await response.json();


            if (!response.ok) {
                throw new Error(
                    result.detail
                    || "Publish failed."
                );
            }


            window.location.href =
                result.redirect_url;

        } catch (error) {

            alert(error.message);

            publishButton.disabled = false;

            publishButton.textContent =
                "Publish";
        }
    }
);


/* ==============================
   INSERT CODE BLOCK
   ============================== */

insertCodeButton.addEventListener(
    "click",
    () => {

        const start =
            contentInput.selectionStart;

        const end =
            contentInput.selectionEnd;

        const selected =
            contentInput.value.substring(
                start,
                end
            );

        const codeBlock =
            "```python\n"
            + selected
            + "\n```";


        contentInput.setRangeText(
            codeBlock,
            start,
            end,
            "end"
        );


        contentInput.focus();

        scheduleAutosave();
    }
);


/* ==============================
   TAB / WINDOW LEAVE
   ============================== */

document.addEventListener(
    "visibilitychange",
    () => {

        if (
            document.visibilityState
            === "hidden"
        ) {
            clearTimeout(
                autosaveTimer
            );

            saveDraft();
        }
    }
);


/* ==============================
   INITIAL STATE
   ============================== */

if (draftId) {
    lastSavedData = getPostData();

    setSaveStatus(
        "saved",
        "Saved"
    );
}