<h1>HEAinstaller</h1>

<h2>Version 2.25.07 (Latest)</h2>

<p><strong>HEAinstaller</strong> is a platform-agnostic <em>(WSL/Linux/Darwin)</em> and XDG-compliant Python script that automates the installation of
<a href="https://heasarc.gsfc.nasa.gov/docs/software/heasoft/">HEASoft</a>.</p>

<blockquote>
  <strong>Note:</strong> Only supported on platforms using <em>glibc</em>.
</blockquote>

<hr>

<h2>Installation (Without Manual Virtual Environment Setup)</h2>

<p>If you want the script to automatically manage and install a temporary virtual environment:</p>

<pre><code>
git clone https://github.com/Anish-Sarkar-1001/HEAinstaller.git
cd HEAinstaller
python3 user_install.py
</code></pre>

<p>If you want to manually create or use an existing environment, follow the guide below.</p>

<hr>

<h2>Requirements</h2>

<table>
  <thead>
    <tr><th>Component</th><th>Details</th></tr>
  </thead>
  <tbody>
    <tr><td>Python</td><td>&ge; 3.8</td></tr>
    <tr><td>Environment</td><td>Active Conda or Virtual Environment</td></tr>
    <tr><td>Python Packages</td><td><code>tqdm</code></td></tr>
    <tr><td>Display Server</td><td>Xorg (X11) or Wayland with <code>$DISPLAY</code> set</td></tr>
  </tbody>
</table>

<h3>Setting Up an Environment</h3>

<ul>
  <li><a href="https://docs.python.org/3/library/venv.html">Virtual Environment Setup Guide</a></li>
  <li><a href="https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html">Conda Environment Setup Guide</a></li>
</ul>

<blockquote>
  <strong>Note:</strong> If no active Conda/Virtual environment is detected, the script will use <code>pip</code> to install Python libraries.
  However, using a Conda/Virtual environment is preferred.
</blockquote>

<hr>

<h2>Installation Guide</h2>

<pre><code>git clone https://github.com/Anish-Sarkar-1001/HEAinstaller.git
cd HEAinstaller
python3 heainstaller.py
</code></pre>

<blockquote>
  <strong>Note:</strong> You will be prompted for your superuser password and asked to provide the <code>heasoft-x.xx.x.tar.gz</code> path if you have already downloaded it.
</blockquote>

<p>After installation, initialize HEASoft with:</p>

<pre><code>heainit</code></pre>

<hr>

<h2>Important Notes</h2>

<ul>
  <li><code>sudo</code> is used. Install it manually on Alpine or other minimal systems.</li>
  <li>Setup is done <strong>without lynx</strong> to avoid errors in some distributions.</li>
</ul>

<hr>

<h2>Customization & Additional Information</h2>

<ul>
  <li>The script is XDG-compliant and installs HEASoft at: <code>$HOME/.local/bin/heasoft</code></li>
  <li>The downloaded tarball will be stored at: <code>$XDG_CACHE_HOME/heasoft.tar.gz</code></li>
  <li>Edit <code>user.json</code> to skip installing specific HEASoft packages by setting values from <code>yes</code> to <code>no</code>.</li>
  <li>Refer to the <a href="https://heasarc.gsfc.nasa.gov/docs/software/lheasoft/download-go.html">HEASoft official documentation</a> for dependency information.</li>
  <li>Progress bars are approximate (±1%).</li>
</ul>

<hr>

<h2>Tested Platforms</h2>

<table>
  <thead>
    <tr><th>Platform</th><th>Versions</th></tr>
  </thead>
  <tbody>
    <tr><td>macOS (Darwin)</td><td>Sequoia, Sonoma, Ventura</td></tr>
    <tr><td>Linux</td><td>Ubuntu, OpenSUSE, Arch, Void (glibc), Gentoo (glibc), Debian, Deepin, Kali, Oracle, CentOS, AlmaLinux, Manjaro</td></tr>
    <tr><td>WSL</td><td>All of the above Linux distributions</td></tr>
  </tbody>
</table>

<hr>

<h2>Supported Shells</h2>

<table>
  <tbody>
    <tr>
      <td>bash</td><td>zsh</td><td>ksh</td><td>dash</td>
      <td>ash</td><td>elvish</td><td>csh</td><td>tcsh</td>
    </tr>
  </tbody>
</table>

<hr>

<h2>Unsupported Platforms</h2>

<table>
  <thead>
    <tr><th>Platform</th><th>Reason</th></tr>
  </thead>
  <tbody>
    <tr><td>Slackware</td><td>Manual configuration required</td></tr>
    <tr><td><code>musl</code> based distros</td><td>Requires <code>glibc</code></td></tr>
  </tbody>
</table>
