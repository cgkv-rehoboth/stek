var gulp = require('gulp'),
    gutil = require('gulp-util'),
    sass = require('gulp-sass'),
    rename = require('gulp-rename'),
    path = require('path'),
    watch = require('gulp-watch'),
    source = require('vinyl-source-stream'),
    buffer = require('vinyl-buffer'),
    livereload = require('gulp-livereload'),
    watchify = require('watchify'),
    browserify = require('browserify'),
    babelify = require('babelify'),
    glob = require('glob')
    sourcemaps = require('gulp-sourcemaps'),
    uglify = require('gulp-uglify');

var assets = path.join(__dirname, 'src/assets');
var scripts = path.join(assets, 'scripts');
var fonts = path.join(assets, 'resources/fonts/**/*');
var images = path.join(assets, 'resources/images/**/*');
var dist = path.join(__dirname, 'dist');
var css = path.join(assets, 'css/**/*');

gulp.task('sass', function() {
  gulp.src([
    './src/assets/sass/common.sass',
    './src/assets/sass/main.sass',
    './src/assets/sass/public/main.sass'
  ], {base: './src/assets/sass/'})
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
function compileScripts(watch, entry, production) {
  var sourceMaps = !production;

  // we use browserify to bundle node style modules into a
  // script ready for the browser
  var bundler = browserify({
    entries: [entry],
    debug: sourceMaps,
    paths: ['./node_modules/', scripts],
    extensions: ['.jsx', '.js'],
    cache: {}, packageCache: {}, fullPaths: true,
    sourceMaps: sourceMaps
  });

  // we use babel to transpile es6 syntax and the react jsx syntax
  // down to es5
  bundler.transform(babelify, {presets: ["es2015", "react"]});

  function bundle() {
    var stream = bundler
      .bundle()
      .on("error", function (error) {
        console.error("Error: " + error.message);
      })
      .pipe(source(entry))
      .pipe(buffer())
      .pipe(sourcemaps.init({loadMaps: true}))
      .pipe(uglify())
      .pipe(sourcemaps.write(path.join(dist, 'scripts')))
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
  compileScripts(watch, path.join(scripts, 'app.jsx'), false);
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
