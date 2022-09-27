const path = require("path");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
  entry: "./src/index.js",
  mode: "development",
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /(node_modules|bower_components)/,
        loader: "babel-loader",
        options: { presets: ["@babel/env"] }
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"]
      }
    ]
  },
  resolve: { extensions: ["*", ".js", ".jsx"] },
  output: {
    // the target directory for all output files
    // must be an absolute path (use the Node.js path module)
    path: path.resolve(__dirname, "../static/js/"),
    // the url to the output directory resolved relative to the HTML page
    // (when executed in the browser, webpack needs to know
    // where you'll host the generated bundle)
    publicPath: "/static/js/",
    filename: "main.js"
  },
  devServer: {
    port: 3000,
    static: [
      {
        // webpack-dev-server will serve the static files in this folder
        // it'll watch your source (js, jsx, css) files, and recompile
        // the bundle whenever they are changed
        // then serve the recompiled bundle from memory
        // (from output.publicPath)
        directory: path.join(__dirname, "../templates"),
      },
    ],
    hot: true
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: path.join(__dirname, "public", "index.html"),
      filename: path.resolve(__dirname, "../templates/index.html"),
    }),
  ]
};