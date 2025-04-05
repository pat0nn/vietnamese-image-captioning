import { MdCheckCircle, MdContentCopy, MdCheck } from "react-icons/md";
import styles from "../styles/success.module.css";
import testImage from "../public/images/FSiE4wdXEAAGkRb.jpeg";
import Head from "next/head";
import { useRouter } from "next/router";
import { useState } from "react";

const Success = () => {

  const router = useRouter();
  let {id, clientImg} = router.query;
  let [isCopied, setCopied] = useState(false);

  let handleCopyLinkClick = (e) => {
    navigator.clipboard.writeText(`https://image-uploader-f08q.onrender.com/image/${id}`).then(() => {
      setCopied(true);
      setTimeout(() => {
        setCopied(false)
      }, 4000);
    })
    console.log("Đã sao chép liên kết")
  }
  
  return (
    <>
      <Head>
        <title>Tải lên hình ảnh thành công!</title>
      </Head>
      <main className={styles.container}>
        <MdCheckCircle />
        <h1>Tải lên thành công!</h1>
        <div className={styles.imgContainer}>
          <img
            src={clientImg}
            alt="Hình ảnh đã tải lên từ thiết bị của bạn"
            width={375}
            height={500}
            style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
          />
        </div>
        <div className={styles.copyLinkContainer}>
          <p>{`https://image-uploader-f08q.onrender.com/image/${id}`}</p>
          <button className={isCopied ? styles.btnCopied : styles.copyBtn} onClick={(e) => handleCopyLinkClick(e)}>
            {isCopied ? <MdCheck /> : <MdContentCopy /> } 
          </button>
        </div>
      </main>
    </>
  );
}

export default Success;