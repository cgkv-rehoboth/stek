[![Stories in Ready](https://badge.waffle.io/cgkv-rehoboth/stek.png?label=ready&title=Ready)](https://waffle.io/cgkv-rehoboth/stek)
# CGKV Woerden Site

<img src="https://raw.githubusercontent.com/cgkv-rehoboth/stek/master/src/assets/resources/images/logo-zwart.png" width="200" />

### Contributing

Just follow the [GitHub Flow](https://guides.github.com/introduction/flow/index.html)

### Getting started

See `docs/getting-started/` for a concise guide on development.

Add a timetable called 'Diensten'

### Production

Make sure...

- ... the server's user has read/write access to the media directory
- ... you have build the staticfiles using in production mode `gulp build:prod`
- ...that the file `src/cgkv/localsettings.py` exists that sets `DEBUG = False` and a secret
db user/password
- ...that you have run `./manage.py collectstatic`

Everytime the staticfiles change, you have to run `collectstatic` and restart the wsgi process.

## Apps

### Fiber 
[Documentation](https://django-fiber.readthedocs.io/en/master/index.html) - [GitHub](https://github.com/django-fiber/django-fiber)

##### Setup
Use Fiber to generate pages with custom content, which can be editted inline or in the admin. All public pages use Fiber, so when installing Django, make sure you create the following pages inside Fiber OR you just apply the fixture from `src/base/fixtures/fiber_001.json` with the command:
`python src/manage.py loaddata fiber_001.json`. When loaded, you are done setting up and you can skip these next steps:
1. Create the pages in Fiber directing to the following URLs (actually the named route is used). These are hardcoded in the public views.py. 
  - `"index"`
  - `"kerktijden"`
  - `"kindercreche"`
  - `"orgel"`
  - `"anbi"`
2. Navigate to the pages on the frontend and add on each page the corresponding `title` and `content`. When hovering over their position, a grey plus button will appear. The tooltip of this button will tell you which block you are adding.  
Only one block of each element can be added. So only one `title`. In the admin, multiple blocks with the same name can be added, but this is discommended. On the frontend, the plus button will also disappear when one element is added to a block.
3. Add an contentitem via the admin, named `nieuwsberichten`. The content of this contentitem will be displayed via the dashboard template. 

##### Fiber commands
The text is displayed on the pages through the Fiber template command `{% show_page_content <block name> %}`, so the name of the contentitems will not influence this. Only the newsfeed uses `{% show_content <contentitem name> %}`, which depends on the contentitem named exactly `nieuwsberichten`. This item can be displayed on any page with the `{% show_content 'nieuwsberichten' %}` command.

##### Hardcoded fallback
A fallback option is available for each page created at 1. This means the Fiber content won't be shown and the hardcoded page (may be outdated) will be displayed on those pages. This is done by setting the page's template to the corresponding 'Vaste \<page\>' template. Only the default template will use Fibers content.
  
##### Page title
Default, the page title (if available) will be as the browser window title, following by ' - Rehobothkerk Woerden'. When the `hide_title` setting is set to 'ja', only 'Rehobothkerk Woerden' will be displayed as the browser window title.

##### Custom pages
Additional pages can be created, but their URL setting must be set to the absolute URL (with a leading slash) or a relative URL (withouth leading slash, not recommended). 

The front page (`"index"`) uses a custom template, which allows it to control multiple title and content blocks. 

##### Jaarthema items

Also, items for 'Jaarthema' can be added by creating a new contentitem. This item must be hooked to the block named 'jaarthema_content' and it's sort number must be the the corresponding year. Also, on the newest (based on the sort number) 'jaarthema' contentitem will be used to determine if the 'jaarthema' section will be shown. This can be configured by the `hide_jaarthema` setting of the contentitem. Thus the latest 'jaarthema' contentitem `hide_jaarthema` setting will determine the visibility of the whole section. The configuration of older contentitems won't have any effect. The `jaarthema_background_url` setting must contain the exact same path as the corresponding image, displayed on the admin page of Fiber images.

##### Overridden functions
In `src/assets/scripts/fiber/admin-extra.js`, some functionallity of Fiber is being overridden. Also, the settings for the CKEditor are being set. These settings are set for the admin pages in `src/base/templates/admin/fiber/change_form.html`.
