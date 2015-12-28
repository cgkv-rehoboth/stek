var gulp = require('gulp'),
    gutil = require('gulp-util'),
    sass = require('gulp-sass'),
    rename = require('gulp-rename'),
    path = require('path'),
    watch = require('gulp-watch'),
    source = require('vinyl-source-stream'),
    livereload = require('gulp-livereload'),
    notify = require('gulp-notify'),
    watchify = require('watchify'),
    browserify = require('browserify'),
    babelify = require('babelify'),
    glob = require('glob');

var assets = path.join(__dirname, 'src/assets');
var scripts = path.join(assets, 'scripts');
var fonts = path.join(assets, 'resources/fonts/**/*');
var images = path.join(assets, 'resources/images/**/*');
var dist = path.join(__dirname, 'dist');
var css = path.join(assets, 'css/**/*');

gulp.task('sass', function() {
  gulp.src('./src/assets/sass/main.sass')
    .pipe(sass({
      includePaths : [
        path.join(__dirname, 'src/assets/fonts'),// sass
        path.join(__dirname, 'src/assets/sass'), // sass
        css,  // css
        path.join(__dirname, 'node_modules/'),
        path.join(__dirname, 'node_modules/font-awesome/scss/')
      ]
    }).on('error', sass.logError))
    .pipe(gulp.dest(path.join(dist, 'css')));
});

// initiates the scripts bundler
function compileScripts(watch, entry) {
  // we use browserify to bundle node style modules into a
  // script ready for the browser
  var bundler = browserify({
    entries: [entry],
    debug: true,
    paths: ['./node_modules/', scripts],
    extensions: ['.jsx', '.js'],
    cache: {}, packageCache: {}, fullPaths: true,
    sourceMaps: true
  });

  // we use babel to transpile es6 syntax and the react jsx syntax
  // down to es5
  bundler.transform(babelify, {presets: ["es2015", "react"]});

  function bundle() {
    var stream = bundler
      .bundle()
      .on("error", notify.onError({
          message: "Error: <%= error.message %>",
          title: "Error building scripts"
      }))
      .pipe(source(entry))
      .pipe(rename(function(fp) {
        // I hate mutating state.
        fp.dirname = "";
        fp.extname = ".js";
      }))
      .pipe(gulp.dest(path.join(dist, 'scripts')));

    stream.on('end', function() { gutil.log("Done building scripts"); });

    return stream;
  };

  // use watchify for fast rebuilds using browserify
  if(watch) {
    bundler = watchify(bundler);
    bundler.on('update', bundle);
  }

  return bundle();
}

function bundleScripts(watch) {
  var entries = glob.sync(path.join(scripts, 'pages/**/*.js')).concat(
        glob.sync(path.join(scripts, 'pages/**/*.jsx')));
  entries.forEach(function(entry) {
    compileScripts(watch, entry);
  });
}

// watch assets and build on changes
gulp.task('watch', function() {
  livereload.listen();

  function initWatch(files, task) {
    gulp.start(task);
    gulp.watch(files, [task]);
  }

  bundleScripts(true);

  initWatch(['./src/assets/sass/**/*.sass', './src/assets/sass/**/*.css'], 'sass');
  initWatch(['./src/assets/css/**/*.css'], 'copy');
});

// copy the assets to the dist
gulp.task('copy', function() {
  return gulp.src([fonts, images, css], {base: assets})
    .pipe(gulp.dest(dist));
});

// run the tasks and start watching by default
gulp.task('default', function() {
  gutil.log(">> Building & standing watch for changes...");
  gulp.start('sass');
  gulp.start('copy');
  bundleScripts(false);
  gulp.start('watch');
});
