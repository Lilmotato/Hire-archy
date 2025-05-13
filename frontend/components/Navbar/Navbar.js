import Link from "next/link";
import styles from "./Navbar.module.css";

export default function Navbar({ navbarLinks }) {
    return (
        <nav className={styles.main}>
            <div className={`${styles.container} ${styles.wrapper}`}>
                <span className={`${styles.logo}`}>
                    <Link href="/">Hire-Archy</Link>
                </span>
                <ul className={styles.ul}>
                    {navbarLinks.map((navbarLink, index) => {
                        return (
                            <li key={index} className={styles.li}>
                                <Link href={navbarLink.value}>{navbarLink.key}</Link>
                            </li>
                        );
                    })}
                </ul>
            </div>
        </nav>
    );
}