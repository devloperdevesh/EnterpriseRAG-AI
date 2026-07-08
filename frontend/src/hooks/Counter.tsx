import {useState, useEffect} from 'react';

export default function Counter({target}: {target: number}) {

  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 1000;
    const increment = target / duration * 10;

    const timer = setInterval(() => {
      start += increment;

      if(start >= target) {
        setCount(target);
        clearInterval(timer);
      }
      else{
        setCount(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  },[target]);

  return <span>{count.toLocaleString()}</span>;
}