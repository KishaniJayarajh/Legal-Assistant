document.getElementById('sidebarToggle')?.addEventListener('click', () => {
  document.getElementById('wrapper')?.classList.toggle('toggled');
});

document.querySelectorAll('.alert').forEach(a => {
  setTimeout(() => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(a);
    bsAlert?.close();
  }, 4000);
});
