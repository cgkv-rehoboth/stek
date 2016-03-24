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
    glob = require('glob'),
    sourcemaps = require('gulp-sourcemaps'),
    uglify = require('gulp-uglify'),
    gzip = require('gulp-gzip'),
    chalk = require('chalk');


var assets = path.join(__dirname, 'src/assets');
var scripts = path.join(assets, 'scripts');
var fonts = path.join(assets, 'resources/fonts/**/*');
var images = path.join(assets, 'resources/images/**/*');
var dist = path.join(__dirname, 'dist');
var css = path.join(assets, 'css/**/*');

function map_error(err) {
  if (err.fileName) {
    // regular error
    gutil.log(chalk.red(err.name)
              + ': '
              + chalk.yellow(err.fileName.replace(__dirname + '/src/js/', ''))
              + ': '
              + 'Line '
              + chalk.magenta(err.lineNumber)
              + ' & '
              + 'Column '
              + chalk.magenta(err.columnNumber || err.column)
              + ': '
              + chalk.blue(err.description));
  } else {
    // browserify error..
    gutil.log(chalk.red(err.name)
              + ': '
              + chalk.yellow(err.message));
  }

  this.end();
}

gulp.task('build:sass', function() {
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

function make_bundler(entry, production) {
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

  return bundler;
}

// initiates the scripts bundler
function bundle(bundler, entry, production) {
  var stream = bundler
    .bundle()
    .on("error", function (error) {
      console.error("Error: " + error.message);
    })
    .pipe(source(entry))
    .pipe(buffer())
    .pipe(rename(function(fp) {
      // I hate mutating state.
      fp.dirname = "";
      fp.extname = ".js";
    }));

  // uglify in production mode
  if(production) {
    stream = stream.pipe(uglify());
  }

  stream = stream.pipe(gulp.dest(path.join(dist, 'scripts')));

  stream.on('end', function() {
    gutil.log(chalk.green("Done building scripts"));
  });

  return stream;
};

gulp.task('build:scripts:dev', function() {
  var entry = path.join(scripts, 'app.jsx');
  var bundler = make_bundler(entry, false);
  bundle(bundler, entry, false);
});

gulp.task('build:scripts:watch', function() {
  // use watchify for fast rebuilds using browserify
  var entry = path.join(scripts, 'app.jsx');
  var bundler = watchify(make_bundler(entry, false));
  bundler.on('update', function() {
    bundle(bundler, entry, false);
  });
  bundle(bundler, entry, false);
});

gulp.task('build:scripts:gzip', function() {
  gulp.src(path.join(dist, 'scripts', '*.js'))
    .pipe(gzip())
    .pipe(gulp.dest(path.join(dist, 'scripts')));
});

gulp.task('build:scripts:prod', function() {
  // use watchify for fast rebuilds using browserify
  var entry = path.join(scripts, 'app.jsx');
  var bundler = make_bundler(entry, true);
  var stream = bundle(bundler, entry, true);

  // gzip the results
  stream.on('end', function() {
    gulp.start('build:scripts:gzip');
  });
});

gulp.task('build:static', function() {
  return gulp.src([fonts, images, css], {base: assets})
    .pipe(gulp.dest(dist));
});

// watch assets and build on changes
gulp.task('watch', function() {
  livereload.listen();

  function initWatch(files, task) {
    gulp.start(task);
    gulp.watch(files, [task]);
  }

  // initial build and watch scripts
  gulp.start('build:scripts:watch');

  // watch sass and css libraries
  initWatch(['./src/assets/sass/**/*.sass', './src/assets/sass/**/*.css'], 'build:sass');
  initWatch(['./src/assets/css/**/*.css'], 'build:static');
});

gulp.task('default', function() {
  gutil.log(">> Building & standing watch for changes...");
  gulp.start('watch');
});

gulp.task('build:prod', function() {
  gulp.start('build:sass');
  gulp.start('build:static');
  gulp.start('build:scripts:prod');
});
