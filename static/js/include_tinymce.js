tinymce.init({
    selector: 'textarea#answer',  // ID вашего textarea
    license_key: 'gpl',
    menubar: false,
    plugins: [
      'autolink lists link image charmap print preview anchor',
      'visualblocks code fullscreen',
      'media table paste code help wordcount'
    ],
    toolbar: 'undo redo | formatselect | ' +
    'bold italic backcolor | alignleft aligncenter ' +
    'alignright alignjustify | bullist numlist outdent indent | ' +
    'removeformat | help',
    content_css: '//www.tiny.cloud/css/codepen.min.css'
 });
document.addEventListener('focusin', (e) => {
    if (e.target.closest(".tox-tinymce, .tox-tinymce-aux, .moxman-window, .tam-assetmanager-root") !== null) {
        e.stopImmediatePropagation();
    }
});