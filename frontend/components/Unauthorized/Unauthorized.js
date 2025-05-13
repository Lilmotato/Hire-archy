import Wrapper from "../Wrapper/Wrapper";
import Link from "next/link";
import styles from "./Unauthorized.module.css";

export default function Unauthorized() {
  return (
    <Wrapper>
      <div className={styles.container}>
        <h1>Unauthorized Access</h1>
        <p>You do not have permission to view this page.</p>
        <Link href="/">
          <button className={styles.button}>Go to Homepage</button>
        </Link>
      </div>
    </Wrapper>
  );
}
