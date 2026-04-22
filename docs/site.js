AOS.init({
  duration: 700,
  once: true,
  offset: 80,
});

const REPO_URL = "https://github.com/YOUR_USERNAME/YOUR_REPOSITORY";

for (const id of ["repo-link-nav", "repo-link-hero"]) {
  const el = document.getElementById(id);
  if (el) {
    el.href = REPO_URL;
  }
}
