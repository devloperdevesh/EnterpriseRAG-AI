export const isAuth = () => {
    return !!localStorage.getItem("token");
  };