function switchTab(tab) {
    const loginForm = document.getElementById('form-login');
    const regForm = document.getElementById('form-register');
    const tabLogin = document.getElementById('tab-login');
    const tabReg = document.getElementById('tab-register');

    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        regForm.classList.add('hidden');
        tabLogin.className = "flex-1 text-center font-bold text-indigo-600 border-b-2 border-indigo-600 pb-2";
        tabReg.className = "flex-1 text-center font-bold text-slate-400 pb-2";
    } else {
        loginForm.classList.add('hidden');
        regForm.classList.remove('hidden');
        tabReg.className = "flex-1 text-center font-bold text-indigo-600 border-b-2 border-indigo-600 pb-2";
        tabLogin.className = "flex-1 text-center font-bold text-slate-400 pb-2";
    }
}