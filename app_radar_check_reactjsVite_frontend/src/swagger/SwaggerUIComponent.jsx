import React from "react";
import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";

const SwaggerUIComponent = () => {
  return <SwaggerUI url="/swagger.json" />;
};

export default SwaggerUIComponent;
