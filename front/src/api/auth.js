import api from './index';

export async function login(usuarioOrEmail, clave){
  // expects { token, user }
  const res = await api.post('/auth/login', { usuario: usuarioOrEmail, clave });
  return res.data;
}
