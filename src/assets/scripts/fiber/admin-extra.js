/**
 * Created by samuel on 20-9-17.
 */

/*
  Override default CKEditor settings of Fiber
  */

window.CKEDITOR_CONFIG_FORMAT_TAGS = 'p;h1;h2;h3;h4';

// Allow also <div> with [attributes], {styles} and (classes)
window.CKEDITOR_CONFIG_EXTRA_ALLOWED_CONTENT = 'a[*]{*}(*);img[*]{*}(*);iframe[*];object[*];param[*];embed[*];div[*]{*}(*);small';

// Add some bootstrap grid styles
window.CKEDITOR_CONFIG_STYLES_SET = [
    { name: 'Streepje', element: '&shy;' },
    { name: 'Subtitle', element: 'small' },
    { name: 'Grid - row', element: 'div', attributes: { 'class': 'row' } },
    { name: 'Grid - col-md-1', element: 'div', attributes: { 'class': 'col-md-1' } },
    { name: 'Grid - col-md-2', element: 'div', attributes: { 'class': 'col-md-2' } },
    { name: 'Grid - col-md-3', element: 'div', attributes: { 'class': 'col-md-3' } },
    { name: 'Grid - col-md-4', element: 'div', attributes: { 'class': 'col-md-4' } },
    { name: 'Grid - col-md-6', element: 'div', attributes: { 'class': 'col-md-6' } },
    { name: 'Grid - col-md-8', element: 'div', attributes: { 'class': 'col-md-8' } },
    { name: 'Grid - col-md-10', element: 'div', attributes: { 'class': 'col-md-10' } },
    { name: 'Grid - col-md-12', element: 'div', attributes: { 'class': 'col-md-12' } }
];
