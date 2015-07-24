es6ify = require('es6ify');

module.exports = function(grunt) {

  var ts_config = {
    module: 'amd', //or commonjs
    target: 'es5', //or es3
    basePath: 'src/client/scripts/',
    sourceMap: true,
    declaration: true
  };

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    // grunt watch config
    watch: {
      scripts: {
        files: [
          'src/client/scripts/**/*.js',
          'src/client/scripts/**/*.jsx'
        ],
        tasks: ['browserify'],
        options: {
          spawn: false,
          livereload: true
        },
      },

      styles: {
        files: [
          'src/client/style/**/*.sass',
          'src/client/style/**/*.scss'
        ],
        tasks: ['compass:dist'],
        options: {
          spawn: false,
          livereload: true
        },
      },

      html: {
        files: [
          'src/client/*.jade',
          'src/client/views/**/*.jade'
        ],
        tasks: ['jade'],
        options: {
          spawn: false,
          livereload: true
        },
      }
    },

    connect: {
      server: {
        options: {
          port: 8000,
          hostname: '*',
          keepalive: true,
          base: 'dist',
          livereload: true
        }
      }
    },

    compass: {
      dist: {
        options: {
          importPath: [
            'src/client/style/bootstrap/'
          ],
          fontsDir: 'src/client/resources/fonts',
          httpFontsDir: 'resources/fonts',
          sassDir: 'src/client/style',
          cssDir: 'dist/style',
        }
      }
    },

    jade: {
      dist: {
        options: {
          data: {
            debug: false
          }
        },

        files: [{
          expand: true,
          src: ["*.jade", "views/**/*.jade"],
          dest: "dist/",
          cwd: "src/client/",
          ext: '.html'
        }]
      }
    },

    copy: {
      resources: {
        files: [{
          expand: true,
          src: ['**/*'],
          cwd: 'src/client/resources',
          dest: 'dist/resources'
        }]
      },
      html: {
        files: [{
          expand: true,
          src: ['index.html', 'views/**/*.html'],
          cwd: 'src/client/',
          dest: 'dist/'
        }]
      }
    },

    browserify: {
      options: {

        transform: [
          require('grunt-react').browserify,

          es6ify.configure(/^(?!.*node_modules)+.+\.js$/)
        ]
      },

      client: {
        src: [es6ify.runtime, 'src/client/scripts/main.js'],
        dest: 'dist/scripts/main.js'
      }
    },

    compress: {
      main: {
        options: {
          archive: 'cgkv-client.tgz'
        },
        files : [
          {
            expand: true,
            cwd: 'dist',
            src: [
              'images/**/*',
              'style/**/*.css',
              'style/fonts/**/*',
              'views/**/*',
              'index.html',
              'scripts/Main.js',
            ]
          }
        ]
      }
    }

  });

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-compass');
  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.loadNpmTasks('grunt-contrib-compress');
  grunt.loadNpmTasks('grunt-contrib-jade');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-notify');
  grunt.loadNpmTasks('grunt-browserify');

  // Default task(s).
  grunt.registerTask('default', [
    'compass:dist',
    'jade',
    'browserify',
    'copy'
  ]);

};
